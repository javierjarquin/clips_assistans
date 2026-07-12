"""Gestión de archivos locales: qué hay en disco y cuánto pesa, para poder
borrarlo desde la app en vez de tocar la carpeta a mano — eso desincroniza la
base de datos (registros apuntando a archivos que ya no existen).
"""

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from shorts_factory.ports.repository import (
    ChannelRepository,
    ClipRepository,
    DownloadRepository,
    VideoRepository,
)


@dataclass(frozen=True)
class ClipAsset:
    clip_id: int
    file_path: str | None
    exists: bool
    size_bytes: int | None


@dataclass(frozen=True)
class VideoAsset:
    video_id: int
    youtube_video_id: str
    title: str
    channel_name: str
    status: str
    raw_path: str | None
    raw_exists: bool
    raw_size_bytes: int | None
    clips: list[ClipAsset] = field(default_factory=list)

    @property
    def total_size_bytes(self) -> int:
        return (self.raw_size_bytes or 0) + sum(c.size_bytes or 0 for c in self.clips)


class ListMediaAssets:
    def __init__(
        self,
        video_repo: VideoRepository,
        channel_repo: ChannelRepository,
        download_repo: DownloadRepository,
        clip_repo: ClipRepository,
    ) -> None:
        self._videos = video_repo
        self._channels = channel_repo
        self._downloads = download_repo
        self._clips = clip_repo

    def execute(self) -> list[VideoAsset]:
        return [self._build(video) for video in self._videos.list_all()]

    def _build(self, video) -> VideoAsset:
        channel = self._channels.get(video.channel_id)
        raw_path = None
        for download in reversed(self._downloads.list_by_video(video.id)):
            if download.file_path:
                raw_path = download.file_path
                break
        raw_exists = bool(raw_path and Path(raw_path).exists())
        raw_size = Path(raw_path).stat().st_size if raw_exists else None

        clip_assets = []
        for clip in self._clips.list_by_video(video.id):
            exists = bool(clip.file_path and Path(clip.file_path).exists())
            size = Path(clip.file_path).stat().st_size if exists else None
            clip_assets.append(ClipAsset(clip.id, clip.file_path, exists, size))

        return VideoAsset(
            video_id=video.id,
            youtube_video_id=video.youtube_video_id,
            title=video.title,
            channel_name=channel.name if channel else "(canal desconocido)",
            status=video.status.value,
            raw_path=raw_path,
            raw_exists=raw_exists,
            raw_size_bytes=raw_size,
            clips=clip_assets,
        )


class DeleteVideoFiles:
    """Borra la carpeta del video en disco (raw.mp4 + clips/) y su historial en la BD."""

    def __init__(self, video_repo: VideoRepository, download_repo: DownloadRepository) -> None:
        self._videos = video_repo
        self._downloads = download_repo

    def execute(self, video_id: int) -> bool:
        """Devuelve True si había una carpeta en disco y se borró."""
        raw_path: Path | None = None
        for download in reversed(self._downloads.list_by_video(video_id)):
            if download.file_path:
                raw_path = Path(download.file_path)
                break
        deleted = False
        if raw_path is not None and raw_path.parent.exists():
            shutil.rmtree(raw_path.parent, ignore_errors=True)
            deleted = True
        self._videos.remove(video_id)
        return deleted


class DeleteClipFile:
    def __init__(self, clip_repo: ClipRepository) -> None:
        self._clips = clip_repo

    def execute(self, clip_id: int) -> bool:
        """Devuelve True si había un archivo en disco y se borró."""
        clip = self._clips.get(clip_id)
        if clip is None:
            return False
        deleted = False
        if clip.file_path and Path(clip.file_path).exists():
            Path(clip.file_path).unlink()
            deleted = True
        self._clips.remove(clip_id)
        return deleted
