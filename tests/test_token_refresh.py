"""Tests del flujo de renovación de tokens de TikTok y X con HTTP simulado."""

from pathlib import Path

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
