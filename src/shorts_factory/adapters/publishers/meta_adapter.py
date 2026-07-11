"""Adaptadores de Meta Graph API: Facebook Reels e Instagram Reels.

Credenciales reales (verificadas jul-2026): ambas redes operan con el
PAGE ACCESS TOKEN long-lived (~60 días) de la página de Facebook vinculada;
los permisos de Instagram van scoped a través de esa página (cuenta
empresa/creador). El App ID + App Secret se guardan para renovar el token
antes del día 60 (fb_exchange_token). Requiere permisos instagram_basic e
instagram_content_publish aprobados en App Review (2-4 semanas).

Facebook Reels (flujo de 3 pasos sobre /{page_id}/video_reels):
  start -> upload binario a rupload.facebook.com -> finish(PUBLISHED)
Instagram Reels (carga resumable local, sin URL pública):
  crear contenedor REELS -> subir binario -> poll status_code -> /media_publish
"""

import logging
import time
from pathlib import Path

import requests

from shorts_factory.domain.entities.publication import Platform
from shorts_factory.ports.publisher import PublisherPort, PublishOutcome

logger = logging.getLogger(__name__)

_TIMEOUT = 120  # subir video tarda; margen amplio


class FacebookReelsPublisher(PublisherPort):
    def __init__(
        self,
        page_id: str | None,
        page_access_token: str | None,
        graph_version: str = "v23.0",
        session: requests.Session | None = None,
    ) -> None:
        self._page_id = page_id
        self._token = page_access_token
        self._version = graph_version
        self._http = session or requests.Session()

    @property
    def platform(self) -> Platform:
        return Platform.FACEBOOK

    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        if not self._page_id or not self._token:
            return PublishOutcome(
                success=False, error="Facebook no configurado (page_id y page_access_token)"
            )
        base = f"https://graph.facebook.com/{self._version}/{self._page_id}/video_reels"
        try:
            start = self._http.post(
                base,
                data={"upload_phase": "start", "access_token": self._token},
                timeout=_TIMEOUT,
            )
            start.raise_for_status()
            video_id = start.json()["video_id"]

            file_size = clip_path.stat().st_size
            with clip_path.open("rb") as fh:
                upload = self._http.post(
                    f"https://rupload.facebook.com/video-upload/{self._version}/{video_id}",
                    headers={
                        "Authorization": f"OAuth {self._token}",
                        "offset": "0",
                        "file_size": str(file_size),
                    },
                    data=fh,
                    timeout=_TIMEOUT * 5,
                )
            upload.raise_for_status()

            finish = self._http.post(
                base,
                data={
                    "upload_phase": "finish",
                    "video_id": video_id,
                    "video_state": "PUBLISHED",
                    "description": caption,
                    "access_token": self._token,
                },
                timeout=_TIMEOUT,
            )
            finish.raise_for_status()
            return PublishOutcome(
                success=True, post_url=f"https://www.facebook.com/reel/{video_id}"
            )
        except requests.RequestException as exc:
            return PublishOutcome(success=False, error=_describe(exc))


class InstagramReelsPublisher(PublisherPort):
    def __init__(
        self,
        ig_user_id: str | None,
        page_access_token: str | None,
        graph_version: str = "v23.0",
        session: requests.Session | None = None,
    ) -> None:
        self._ig_user_id = ig_user_id
        self._token = page_access_token
        self._version = graph_version
        self._http = session or requests.Session()

    @property
    def platform(self) -> Platform:
        return Platform.INSTAGRAM

    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        if not self._ig_user_id or not self._token:
            return PublishOutcome(
                success=False,
                error="Instagram no configurado (ig_user_id y page_access_token)",
            )
        graph = f"https://graph.facebook.com/{self._version}"
        try:
            container = self._http.post(
                f"{graph}/{self._ig_user_id}/media",
                data={
                    "media_type": "REELS",
                    "upload_type": "resumable",
                    "caption": caption,
                    "access_token": self._token,
                },
                timeout=_TIMEOUT,
            )
            container.raise_for_status()
            payload = container.json()
            container_id, upload_uri = payload["id"], payload["uri"]

            file_size = clip_path.stat().st_size
            with clip_path.open("rb") as fh:
                upload = self._http.post(
                    upload_uri,
                    headers={
                        "Authorization": f"OAuth {self._token}",
                        "offset": "0",
                        "file_size": str(file_size),
                    },
                    data=fh,
                    timeout=_TIMEOUT * 5,
                )
            upload.raise_for_status()

            # El contenedor procesa el video async: esperar FINISHED antes de publicar
            for _ in range(30):
                status = self._http.get(
                    f"{graph}/{container_id}",
                    params={"fields": "status_code", "access_token": self._token},
                    timeout=_TIMEOUT,
                )
                status.raise_for_status()
                code = status.json().get("status_code")
                if code == "FINISHED":
                    break
                if code == "ERROR":
                    return PublishOutcome(
                        success=False, error="Instagram: el contenedor terminó en ERROR"
                    )
                time.sleep(2)

            publish = self._http.post(
                f"{graph}/{self._ig_user_id}/media_publish",
                data={"creation_id": container_id, "access_token": self._token},
                timeout=_TIMEOUT,
            )
            publish.raise_for_status()
            media_id = publish.json().get("id", "")

            post_url = None
            permalink = self._http.get(
                f"{graph}/{media_id}",
                params={"fields": "permalink", "access_token": self._token},
                timeout=_TIMEOUT,
            )
            if permalink.ok:
                post_url = permalink.json().get("permalink")
            return PublishOutcome(success=True, post_url=post_url or f"ig-media:{media_id}")
        except requests.RequestException as exc:
            return PublishOutcome(success=False, error=_describe(exc))


def _describe(exc: requests.RequestException) -> str:
    detail = ""
    if exc.response is not None:
        detail = f" — {exc.response.status_code}: {exc.response.text[:300]}"
    return f"{type(exc).__name__}{detail}"
