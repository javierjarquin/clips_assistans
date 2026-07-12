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

Renovación de token (MetaTokenRefresher): a diferencia de TikTok/X, Meta no
tiene grant_type=refresh_token para el token de página — hay que re-derivarlo
de un USER access token de larga duración vía /me/accounts. Como el token de
página dura ~60 días (no horas), no vale la pena renovarlo en cada publicación
como hacen TikTok/X: se renueva bajo demanda, solo cuando Meta lo rechaza
(error 190, OAuthException) y se reintenta una vez.
"""

import logging
import time
from collections.abc import Callable
from pathlib import Path

import requests

from shorts_factory.domain.entities.publication import Platform
from shorts_factory.ports.publisher import PublisherPort, PublishOutcome

logger = logging.getLogger(__name__)

_TIMEOUT = 120  # subir video tarda; margen amplio


def _is_expired_token_error(exc: requests.RequestException) -> bool:
    if exc.response is None:
        return False
    try:
        error = exc.response.json().get("error", {})
    except ValueError:
        return False
    return error.get("code") == 190 or error.get("type") == "OAuthException"


class MetaTokenRefresher:
    """Re-deriva el Page Access Token a partir de un User Access Token de larga duración.

    Cadena: intercambia el user token guardado por uno fresco de ~60 días
    (fb_exchange_token) y pide /me/accounts con ese token para sacar el page
    token actualizado. Persiste ambos vía on_tokens (mismo patrón que TikTok/X).
    """

    def __init__(
        self,
        app_id: str | None,
        app_secret: str | None,
        user_access_token: str | None,
        page_id: str | None,
        graph_version: str = "v23.0",
        on_tokens: Callable[[dict[str, str]], None] | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._app_id = app_id
        self._app_secret = app_secret
        self._user_token = user_access_token
        self._page_id = page_id
        self._version = graph_version
        self._on_tokens = on_tokens
        self._http = session or requests.Session()

    def can_refresh(self) -> bool:
        return bool(self._app_id and self._app_secret and self._user_token and self._page_id)

    def refresh(self) -> str | None:
        """Devuelve el nuevo page access token, o None si no se pudo renovar."""
        if not self.can_refresh():
            logger.warning(
                "Meta: token expirado pero falta SF_META_USER_ACCESS_TOKEN"
                " (u otro dato) para renovarlo automáticamente"
            )
            return None
        graph = f"https://graph.facebook.com/{self._version}"
        try:
            exchange = self._http.get(
                f"{graph}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self._app_id,
                    "client_secret": self._app_secret,
                    "fb_exchange_token": self._user_token,
                },
                timeout=_TIMEOUT,
            )
            exchange.raise_for_status()
            self._user_token = exchange.json()["access_token"]

            accounts = self._http.get(
                f"{graph}/me/accounts",
                params={"access_token": self._user_token},
                timeout=_TIMEOUT,
            )
            accounts.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Meta: falló la renovación del token: %s", _describe(exc))
            return None

        page = next(
            (p for p in accounts.json().get("data", []) if p.get("id") == self._page_id), None
        )
        if page is None:
            logger.error("Meta: la página %s no aparece en /me/accounts al renovar", self._page_id)
            return None

        page_token = page["access_token"]
        logger.info("Meta: token de página renovado automáticamente")
        if self._on_tokens:
            self._on_tokens(
                {
                    "SF_META_USER_ACCESS_TOKEN": self._user_token,
                    "SF_META_PAGE_ACCESS_TOKEN": page_token,
                }
            )
        return page_token


class FacebookReelsPublisher(PublisherPort):
    def __init__(
        self,
        page_id: str | None,
        page_access_token: str | None,
        graph_version: str = "v23.0",
        token_refresher: MetaTokenRefresher | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._page_id = page_id
        self._token = page_access_token
        self._version = graph_version
        self._refresher = token_refresher
        self._http = session or requests.Session()

    @property
    def platform(self) -> Platform:
        return Platform.FACEBOOK

    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        if not self._page_id or not self._token:
            return PublishOutcome(
                success=False, error="Facebook no configurado (page_id y page_access_token)"
            )
        try:
            return self._do_publish(clip_path, caption)
        except requests.RequestException as exc:
            if _is_expired_token_error(exc) and self._refresher and self._refresher.can_refresh():
                new_token = self._refresher.refresh()
                if new_token:
                    self._token = new_token
                    try:
                        return self._do_publish(clip_path, caption)
                    except requests.RequestException as exc2:
                        return PublishOutcome(success=False, error=_describe(exc2))
            return PublishOutcome(success=False, error=_describe(exc))

    def _do_publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        """Propaga requests.RequestException: publish() decide si reintentar tras renovar."""
        base = f"https://graph.facebook.com/{self._version}/{self._page_id}/video_reels"
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
        return PublishOutcome(success=True, post_url=f"https://www.facebook.com/reel/{video_id}")


class InstagramReelsPublisher(PublisherPort):
    def __init__(
        self,
        ig_user_id: str | None,
        page_access_token: str | None,
        graph_version: str = "v23.0",
        token_refresher: MetaTokenRefresher | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._ig_user_id = ig_user_id
        self._token = page_access_token
        self._version = graph_version
        self._refresher = token_refresher
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
        try:
            return self._do_publish(clip_path, caption)
        except requests.RequestException as exc:
            if _is_expired_token_error(exc) and self._refresher and self._refresher.can_refresh():
                new_token = self._refresher.refresh()
                if new_token:
                    self._token = new_token
                    try:
                        return self._do_publish(clip_path, caption)
                    except requests.RequestException as exc2:
                        return PublishOutcome(success=False, error=_describe(exc2))
            return PublishOutcome(success=False, error=_describe(exc))

    def _do_publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        """Propaga requests.RequestException: publish() decide si reintentar tras renovar."""
        graph = f"https://graph.facebook.com/{self._version}"
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


def _describe(exc: requests.RequestException) -> str:
    detail = ""
    if exc.response is not None:
        detail = f" — {exc.response.status_code}: {exc.response.text[:300]}"
    return f"{type(exc).__name__}{detail}"
