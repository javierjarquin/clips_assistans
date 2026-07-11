"""Dobles de prueba compartidos."""

from pathlib import Path

from shorts_factory.ports.video_source import DownloadOutcome, VideoMetadata, VideoSourcePort


class FakeVideoSource(VideoSourcePort):
    """Fuente en memoria: feed configurable por canal, descargas simuladas."""

    def __init__(self) -> None:
        self.feeds: dict[str, list[VideoMetadata]] = {}
        self.fail_download = False
        self.download_calls: list[str] = []

    def list_recent_videos(self, youtube_channel_id: str, limit: int = 10) -> list[VideoMetadata]:
        return self.feeds.get(youtube_channel_id, [])[:limit]

    def download(self, youtube_video_id: str, dest_path: Path) -> DownloadOutcome:
        self.download_calls.append(youtube_video_id)
        if self.fail_download:
            return DownloadOutcome(success=False, method="fake", error="fallo simulado")
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(b"video falso")
        return DownloadOutcome(
            success=True, file_path=dest_path, size_bytes=dest_path.stat().st_size, method="fake"
        )
