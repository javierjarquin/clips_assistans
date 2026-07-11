"""Descarga de videos detectados a /data/{canal}/{video_id}/raw.mp4.

Estados: detected -> downloading -> downloaded | error. Cada intento queda
registrado en downloads con el método que funcionó (o el error).
"""

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from shorts_factory.domain.entities.download import Download, DownloadStatus
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.ports.repository import ChannelRepository, DownloadRepository, VideoRepository
from shorts_factory.ports.video_source import VideoSourcePort

logger = logging.getLogger(__name__)


def slugify(value: str) -> str:
    """Nombre de canal -> nombre de carpeta seguro (ascii, guiones)."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value) or "canal"


@dataclass
class DownloadReport:
    downloaded: list[Video] = field(default_factory=list)
    failed: list[tuple[Video, str]] = field(default_factory=list)


class DownloadVideos:
    def __init__(
        self,
        video_repo: VideoRepository,
        channel_repo: ChannelRepository,
        download_repo: DownloadRepository,
        video_source: VideoSourcePort,
        data_dir: Path,
    ) -> None:
        self._videos = video_repo
        self._channels = channel_repo
        self._downloads = download_repo
        self._source = video_source
        self._data_dir = data_dir

    def execute(self) -> DownloadReport:
        report = DownloadReport()
        for video in self._videos.list_by_status(VideoStatus.DETECTED):
            self._download_one(video, report)
        return report

    def _download_one(self, video: Video, report: DownloadReport) -> None:
        channel = self._channels.get(video.channel_id)
        channel_slug = slugify(channel.name) if channel else f"canal-{video.channel_id}"
        dest = self._data_dir / channel_slug / video.youtube_video_id / "raw.mp4"

        self._videos.update_status(video.id, VideoStatus.DOWNLOADING)
        try:
            outcome = self._source.download(video.youtube_video_id, dest)
        except Exception as exc:  # noqa: BLE001 — el fallo se registra, no tumba el lote
            outcome = None
            error = str(exc)
        else:
            error = outcome.error or "descarga fallida"

        if outcome and outcome.success:
            self._downloads.add(
                Download(
                    video_id=video.id,
                    file_path=str(outcome.file_path),
                    size_bytes=outcome.size_bytes,
                    method=outcome.method,
                    status=DownloadStatus.COMPLETED,
                    completed_at=datetime.now(),
                )
            )
            self._videos.update_status(video.id, VideoStatus.DOWNLOADED)
            report.downloaded.append(video)
            logger.info("Descargado %s (%s bytes)", video.youtube_video_id, outcome.size_bytes)
        else:
            self._downloads.add(
                Download(
                    video_id=video.id,
                    method=outcome.method if outcome else "excepción",
                    status=DownloadStatus.FAILED,
                    error_message=error,
                    completed_at=datetime.now(),
                )
            )
            self._videos.update_status(video.id, VideoStatus.ERROR)
            report.failed.append((video, error))
            logger.error("Falló descarga de %s: %s", video.youtube_video_id, error)
