"""Adaptador de TikTok Content Posting API.

Autenticación real de TikTok (verificada jul-2026):
- El access token dura 24 h; se renueva sin intervención del usuario con
  POST /v2/oauth/token/ (client_key + client_secret + refresh_token).
- El refresh token dura hasta 365 días y ROTA en cada renovación: la respuesta
  trae uno nuevo que hay que persistir (callback on_tokens) o el siguiente
  arranque quedará con un token muerto.
- Sin auditoría aprobada las publicaciones quedan privadas: privacy_level
  por defecto SELF_ONLY.
"""

import logging
from collections.abc import Callable
from pathlib import Path

import requests

from shorts_factory.domain.entities.publication import Platform
from shorts_factory.ports.publisher import PublisherPort, PublishOutcome

logger = logging.getLogger(__name__)

_API = "https://open.tiktokapis.com/v2"
_TIMEOUT = 120
_CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB


class TikTokPublisher(PublisherPort):
    def __init__(
        self,
        client_key: str | None,
        client_secret: str | None,
        refresh_token: str | None,
        access_token: str | None = None,
        privacy_level: str = "SELF_ONLY",
        on_tokens: Callable[[dict[str, str]], None] | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._client_key = client_key
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token = access_token
        self._privacy = privacy_level
        self._on_tokens = on_tokens
        self._http = session or requests.Session()

    @property
    def platform(self) -> Platform:
        return Platform.TIKTOK

    def _configured(self) -> bool:
        return bool(self._client_key and self._client_secret and self._refresh_token)

    def _refresh_access_token(self) -> None:
        response = self._http.post(
            f"{_API}/oauth/token/",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_key": self._client_key,
                "client_secret": self._client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            },
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if "access_token" not in payload:
            raise requests.RequestException(f"TikTok no devolvió access_token: {payload}")
        self._access_token = payload["access_token"]
        rotated = payload.get("refresh_token")
        if rotated and rotated != self._refresh_token:
            self._refresh_token = rotated
            logger.info("TikTok rotó el refresh token; persistiendo")
        if self._on_tokens:
            self._on_tokens(
                {
                    "SF_TIKTOK_ACCESS_TOKEN": self._access_token,
                    "SF_TIKTOK_REFRESH_TOKEN": self._refresh_token or "",
                }
            )

    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        if not self._configured():
            return PublishOutcome(
                success=False,
                error="TikTok no configurado (client_key, client_secret y refresh_token)",
            )
        try:
            # El access dura 24 h y este proceso corre esporádico: renovar siempre
            self._refresh_access_token()
            return self._do_publish(clip_path, caption)
        except requests.RequestException as exc:
            return PublishOutcome(success=False, error=_describe(exc))

    def _do_publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        file_size = clip_path.stat().st_size
        total_chunks = max(1, (file_size + _CHUNK_SIZE - 1) // _CHUNK_SIZE)
        init = self._http.post(
            f"{_API}/post/publish/video/init/",
            headers={"Authorization": f"Bearer {self._access_token}"},
            json={
                "post_info": {"title": caption[:150], "privacy_level": self._privacy},
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": file_size,
                    "chunk_size": min(_CHUNK_SIZE, file_size),
                    "total_chunk_count": total_chunks,
                },
            },
            timeout=_TIMEOUT,
        )
        init.raise_for_status()
        data = init.json()["data"]
        publish_id, upload_url = data["publish_id"], data["upload_url"]

        with clip_path.open("rb") as fh:
            offset = 0
            while offset < file_size:
                chunk = fh.read(_CHUNK_SIZE)
                end = offset + len(chunk) - 1
                upload = self._http.put(
                    upload_url,
                    headers={
                        "Content-Range": f"bytes {offset}-{end}/{file_size}",
                        "Content-Type": "video/mp4",
                    },
                    data=chunk,
                    timeout=_TIMEOUT * 5,
                )
                upload.raise_for_status()
                offset += len(chunk)

        return PublishOutcome(success=True, post_url=f"tiktok-publish:{publish_id}")


def _describe(exc: requests.RequestException) -> str:
    detail = ""
    if exc.response is not None:
        detail = f" — {exc.response.status_code}: {exc.response.text[:300]}"
    return f"{type(exc).__name__}{detail}"
