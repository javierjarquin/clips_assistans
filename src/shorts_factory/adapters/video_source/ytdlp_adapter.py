"""Adaptador de VideoSourcePort basado en yt-dlp.

Escaneo: modo flat-playlist (solo metadatos, rápido y barato).
Descarga: se implementa en Etapa 2.
"""

import logging
from datetime import datetime
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from shorts_factory.ports.video_source import DownloadOutcome, VideoMetadata, VideoSourcePort

logger = logging.getLogger(__name__)


def channel_videos_url(youtube_channel_id: str) -> str:
    """Normaliza ID de canal, handle (@nombre) o URL a la URL de la pestaña Videos."""
    ref = youtube_channel_id.strip()
    if ref.startswith(("http://", "https://")):
        return ref.rstrip("/") + ("" if ref.rstrip("/").endswith("/videos") else "/videos")
    if ref.startswith("@"):
        return f"https://www.youtube.com/{ref}/videos"
    if ref.startswith("UC"):
        return f"https://www.youtube.com/channel/{ref}/videos"
    # Sin prefijo: se asume handle
    return f"https://www.youtube.com/@{ref}/videos"


class YtDlpVideoSource(VideoSourcePort):
    name = "yt-dlp"

    def __init__(
        self,
        extractor_args: dict | None = None,
        cookies_from_browser: str | None = None,
        ffmpeg_location: str | None = None,
    ) -> None:
        self._extractor_args = extractor_args
        self._cookies_from_browser = cookies_from_browser
        self._ffmpeg_location = ffmpeg_location

    def _base_opts(self) -> dict:
        opts: dict = {"quiet": True, "no_warnings": True, "noprogress": True}
        if self._extractor_args:
            opts["extractor_args"] = self._extractor_args
        if self._cookies_from_browser:
            opts["cookiesfrombrowser"] = (self._cookies_from_browser,)
        if self._ffmpeg_location:
            opts["ffmpeg_location"] = self._ffmpeg_location
        return opts

    def list_recent_videos(self, youtube_channel_id: str, limit: int = 10) -> list[VideoMetadata]:
        opts = self._base_opts() | {
            "extract_flat": "in_playlist",
            "playlist_items": f"1:{limit}",
        }
        url = channel_videos_url(youtube_channel_id)
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get("entries") or []
        videos: list[VideoMetadata] = []
        for entry in entries:
            if not entry or not entry.get("id"):
                continue
            timestamp = entry.get("timestamp")
            videos.append(
                VideoMetadata(
                    youtube_video_id=entry["id"],
                    title=entry.get("title") or entry["id"],
                    duration_seconds=int(entry["duration"]) if entry.get("duration") else None,
                    published_at=datetime.fromtimestamp(timestamp) if timestamp else None,
                )
            )
        return videos

    def download(self, youtube_video_id: str, dest_path: Path) -> DownloadOutcome:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        opts = self._base_opts() | {
            # mp4 progresivo o mejor video+audio con merge (requiere ffmpeg)
            "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
            "merge_output_format": "mp4",
            "outtmpl": str(dest_path),
            "overwrites": True,
        }
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={youtube_video_id}"])
        except DownloadError as exc:
            return DownloadOutcome(success=False, method=self.name, error=str(exc))
        if not dest_path.exists():
            return DownloadOutcome(
                success=False, method=self.name, error="descarga terminó sin archivo"
            )
        return DownloadOutcome(
            success=True,
            file_path=dest_path,
            size_bytes=dest_path.stat().st_size,
            method=self.name,
        )
