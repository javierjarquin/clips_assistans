"""Tests del flujo de renovación de tokens de TikTok, X y Meta con HTTP simulado."""

from pathlib import Path

from shorts_factory.adapters.publishers.meta_adapter import (
    FacebookReelsPublisher,
    MetaTokenRefresher,
)
from shorts_factory.adapters.publishers.tiktok_adapter import TikTokPublisher
from shorts_factory.adapters.publishers.x_adapter import XPublisher


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self._payload = payload
        self.status_code = status
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(response=self)


class FakeSession:
    """Devuelve respuestas por prefijo de URL y registra las peticiones."""

    def __init__(self, routes: dict):
        self.routes = routes
        self.requests: list[tuple[str, str, dict]] = []

    def _match(self, method: str, url: str, **kwargs) -> FakeResponse:
        self.requests.append((method, url, kwargs))
        for prefix, response in self.routes.items():
            if url.startswith(prefix):
                return response() if callable(response) else response
        raise AssertionError(f"URL inesperada: {url}")

    def post(self, url, **kwargs):
        return self._match("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self._match("PUT", url, **kwargs)

    def get(self, url, **kwargs):
        return self._match("GET", url, **kwargs)


def test_tiktok_refreshes_and_persists_rotated_token(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    saved: list[dict] = []
    session = FakeSession(
        {
            "https://open.tiktokapis.com/v2/oauth/token/": FakeResponse(
                {"access_token": "acc_nuevo", "refresh_token": "ref_rotado"}
            ),
            "https://open.tiktokapis.com/v2/post/publish/video/init/": FakeResponse(
                {"data": {"publish_id": "p1", "upload_url": "https://upload.tiktok/x"}}
            ),
            "https://upload.tiktok/x": FakeResponse({}),
        }
    )
    publisher = TikTokPublisher(
        "ck", "cs", "ref_viejo", on_tokens=saved.append, session=session
    )

    outcome = publisher.publish(clip, "hola")

    assert outcome.success is True
    assert saved == [
        {"SF_TIKTOK_ACCESS_TOKEN": "acc_nuevo", "SF_TIKTOK_REFRESH_TOKEN": "ref_rotado"}
    ]
    init_call = [r for r in session.requests if "video/init" in r[1]][0]
    assert init_call[2]["headers"]["Authorization"] == "Bearer acc_nuevo"


def test_tiktok_unconfigured_returns_clear_error(tmp_path: Path) -> None:
    outcome = TikTokPublisher(None, None, None).publish(tmp_path / "x.mp4", "hola")
    assert outcome.success is False
    assert "client_key" in outcome.error


def test_x_refresh_rotates_single_use_token(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"v")
    saved: list[dict] = []
    session = FakeSession(
        {
            "https://api.x.com/2/oauth2/token": FakeResponse(
                {"access_token": "acc2h", "refresh_token": "ref_nuevo"}
            ),
            "https://api.x.com/2/media/upload/initialize": FakeResponse(
                {"data": {"id": "m1"}}
            ),
            "https://api.x.com/2/media/upload/m1/append": FakeResponse({}),
            "https://api.x.com/2/media/upload/m1/finalize": FakeResponse(
                {"data": {}}  # sin processing_info => listo
            ),
            "https://api.x.com/2/tweets": FakeResponse({"data": {"id": "t99"}}),
        }
    )
    publisher = XPublisher("cid", "csec", "ref_viejo", on_tokens=saved.append, session=session)

    outcome = publisher.publish(clip, "mira https://spam.com esto")

    assert outcome.success is True
    assert outcome.post_url == "https://x.com/i/status/t99"
    assert saved[0]["SF_X_REFRESH_TOKEN"] == "ref_nuevo"
    # Basic auth de cliente confidencial en la renovación
    token_call = [r for r in session.requests if "oauth2/token" in r[1]][0]
    assert token_call[2]["headers"]["Authorization"].startswith("Basic ")
    # El texto del tweet no lleva enlaces
    tweet_call = [r for r in session.requests if r[1].endswith("/tweets")][0]
    assert "spam.com" not in tweet_call[2]["json"]["text"]


def test_x_unconfigured_returns_clear_error(tmp_path: Path) -> None:
    outcome = XPublisher(None, None, None).publish(tmp_path / "x.mp4", "hola")
    assert outcome.success is False
    assert "client_id" in outcome.error


def test_facebook_renews_expired_page_token_and_retries(tmp_path: Path) -> None:
    """Meta no tiene refresh_token: el token de página se renueva bajo demanda
    (tras un 190/OAuthException), re-derivándolo de un user token de larga
    duración vía /me/accounts — a diferencia de TikTok/X, no en cada llamada.
    """
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    saved: list[dict] = []
    starts: list[str] = []
    session: FakeSession  # forward ref para el closure del route callable

    def video_reels_route():
        data = session.requests[-1][2]["data"]
        if data["upload_phase"] != "start":
            return FakeResponse({})
        starts.append(data["access_token"])
        if len(starts) == 1:  # primer intento: token viejo, Meta lo rechaza
            return FakeResponse(
                {"error": {"code": 190, "type": "OAuthException", "message": "Expired"}},
                status=400,
            )
        return FakeResponse({"video_id": "v1"})

    session = FakeSession(
        {
            "https://graph.facebook.com/v23.0/PAGE1/video_reels": video_reels_route,
            "https://rupload.facebook.com/": FakeResponse({}),
            "https://graph.facebook.com/v23.0/oauth/access_token": FakeResponse(
                {"access_token": "user_largo"}
            ),
            "https://graph.facebook.com/v23.0/me/accounts": FakeResponse(
                {"data": [{"id": "PAGE1", "access_token": "page_nuevo"}]}
            ),
        }
    )
    refresher = MetaTokenRefresher(
        "app_id", "app_secret", "user_viejo", "PAGE1", "v23.0",
        on_tokens=saved.append, session=session,
    )
    publisher = FacebookReelsPublisher(
        "PAGE1", "page_viejo", "v23.0", token_refresher=refresher, session=session
    )

    outcome = publisher.publish(clip, "hola")

    assert outcome.success is True
    assert starts == ["page_viejo", "page_nuevo"]  # reintentó con el token renovado
    assert saved == [
        {"SF_META_USER_ACCESS_TOKEN": "user_largo", "SF_META_PAGE_ACCESS_TOKEN": "page_nuevo"}
    ]


def test_facebook_expired_token_without_refresher_fails_cleanly(tmp_path: Path) -> None:
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video")
    session = FakeSession(
        {
            "https://graph.facebook.com/v23.0/PAGE1/video_reels": FakeResponse(
                {"error": {"code": 190, "type": "OAuthException", "message": "Expired"}},
                status=400,
            ),
        }
    )
    publisher = FacebookReelsPublisher("PAGE1", "page_viejo", "v23.0", session=session)

    outcome = publisher.publish(clip, "hola")

    assert outcome.success is False
    assert "400" in outcome.error


def test_meta_refresher_without_credentials_cannot_refresh() -> None:
    refresher = MetaTokenRefresher(None, None, None, None)
    assert refresher.can_refresh() is False
    assert refresher.refresh() is None
