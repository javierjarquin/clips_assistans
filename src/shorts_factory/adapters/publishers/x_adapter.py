"""Adaptador de X API v2: carga de video en fragmentos + creación del post.

Autenticación real de X (verificada jul-2026), OAuth 2.0 user context con PKCE:
- El access token dura 2 h; se renueva con POST /2/oauth2/token
  (grant_type=refresh_token + client_id; clientes confidenciales agregan
  Basic auth con client_id:client_secret).
- El refresh token es de UN SOLO USO: cada renovación devuelve un refresh
  token nuevo que hay que persistir (callback on_tokens) o la sesión muere.

Costos (pago por uso): publicar sin enlace es ~13x más barato que con enlace,
por eso el adaptador elimina URLs del texto antes de publicar.
"""

import base64
import logging
import re
import time
from collections.abc import Callable
from pathlib import Path

import requests

from shorts_factory.domain.entities.publication import Platform
from shorts_factory.ports.publisher import PublisherPort, PublishOutcome

logger = logging.getLogger(__name__)

_API = "https://api.x.com/2"
_TIMEOUT = 120
_CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB por fragmento (límite de append: 5 MB)
_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def strip_links(text: str) -> str:
    """Quita enlaces del texto: publicar con enlace cuesta ~13x más en X."""
    return _URL_PATTERN.sub("", text).strip()


class XPublisher(PublisherPort):
    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        refresh_token: str | None,
        access_token: str | None = None,
        on_tokens: Callable[[dict[str, str]], None] | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token = access_token
        self._on_tokens = on_tokens
        self._http = session or requests.Session()

    @property
    def platform(self) -> Platform:
        return Platform.X

    def _configured(self) -> bool:
        return bool(self._client_id and self._refresh_token)

    def _refresh_access_token(self) -> None:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self._client_secret:  # cliente confidencial: Basic client_id:client_secret
            basic = base64.b64encode(
                f"{self._client_id}:{self._client_secret}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {basic}"
        response = self._http.post(
            f"{_API}/oauth2/token",
            headers=headers,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self._client_id,
            },
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        self._access_token = payload["access_token"]
        rotated = payload.get("refresh_token")
        if rotated:
            # Un solo uso: el anterior ya quedó inválido, persistir es obligatorio
            self._refresh_token = rotated
            logger.info("X rotó el refresh token; persistiendo")
        if self._on_tokens:
            self._on_tokens(
                {
                    "SF_X_ACCESS_TOKEN": self._access_token,
                    "SF_X_REFRESH_TOKEN": self._refresh_token or "",
                }
            )

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._access_token}"}

    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        if not self._configured():
            return PublishOutcome(
                success=False, error="X no configurado (client_id y refresh_token)"
            )
        caption = strip_links(caption)[:280]
        try:
            # Access de 2 h y proceso esporádico: renovar al inicio de cada publicación
            self._refresh_access_token()
            return self._do_publish(clip_path, caption)
        except requests.RequestException as exc:
            detail = ""
            if exc.response is not None:
                detail = f" — {exc.response.status_code}: {exc.response.text[:300]}"
            return PublishOutcome(success=False, error=f"{type(exc).__name__}{detail}")

    def _do_publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        file_size = clip_path.stat().st_size
        init = self._http.post(
            f"{_API}/media/upload/initialize",
            headers=self._headers(),
            json={
                "media_type": "video/mp4",
                "total_bytes": file_size,
                "media_category": "tweet_video",
            },
            timeout=_TIMEOUT,
        )
        init.raise_for_status()
        media_id = init.json()["data"]["id"]

        with clip_path.open("rb") as fh:
            segment = 0
            while chunk := fh.read(_CHUNK_SIZE):
                append = self._http.post(
                    f"{_API}/media/upload/{media_id}/append",
                    headers=self._headers(),
                    data={"segment_index": segment},
                    files={"media": chunk},
                    timeout=_TIMEOUT * 5,
                )
                append.raise_for_status()
                segment += 1

        finalize = self._http.post(
            f"{_API}/media/upload/{media_id}/finalize",
            headers=self._headers(),
            timeout=_TIMEOUT,
        )
        finalize.raise_for_status()

        # Esperar el procesamiento del video antes de crear el post
        info = finalize.json().get("data", {})
        for _ in range(30):
            state = (info.get("processing_info") or {}).get("state")
            if state in (None, "succeeded"):
                break
            if state == "failed":
                return PublishOutcome(success=False, error="X: procesamiento de video falló")
            time.sleep((info.get("processing_info") or {}).get("check_after_secs", 2))
            status = self._http.get(
                f"{_API}/media/upload",
                headers=self._headers(),
                params={"media_id": media_id, "command": "STATUS"},
                timeout=_TIMEOUT,
            )
            status.raise_for_status()
            info = status.json().get("data", {})

        tweet = self._http.post(
            f"{_API}/tweets",
            headers=self._headers(),
            json={"text": caption, "media": {"media_ids": [str(media_id)]}},
            timeout=_TIMEOUT,
        )
        tweet.raise_for_status()
        tweet_id = tweet.json()["data"]["id"]
        return PublishOutcome(success=True, post_url=f"https://x.com/i/status/{tweet_id}")
