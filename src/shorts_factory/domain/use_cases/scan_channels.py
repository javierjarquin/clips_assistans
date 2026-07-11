"""Escaneo de canales: detecta videos nuevos comparando contra el último conocido.

Primera pasada de un canal (sin last_video_id): establece línea base con el video
más reciente, sin encolar nada — evita inundar el pipeline con videos viejos.
Pasadas siguientes: todo lo publicado después del último conocido entra como
`detected`, sin duplicar registros ya existentes.
"""

import logging
from dataclasses import dataclass, field

from shorts_factory.domain.entities.video import Video
from shorts_factory.ports.repository import ChannelRepository, VideoRepository
from shorts_factory.ports.video_source import VideoSourcePort

logger = logging.getLogger(__name__)


@dataclass
class ChannelScanResult:
    channel_name: str
    new_videos: list[Video] = field(default_factory=list)
    baseline_set: bool = False
    error: str | None = None


class ScanChannels:
    def __init__(
        self,
        channel_repo: ChannelRepository,
        video_repo: VideoRepository,
        video_source: VideoSourcePort,
        scan_limit: int = 10,
    ) -> None:
        self._channels = channel_repo
        self._videos = video_repo
        self._source = video_source
        self._scan_limit = scan_limit

    def execute(self) -> list[ChannelScanResult]:
        results = []
        for channel in self._channels.list_all(active_only=True):
            results.append(self._scan_channel(channel))
        return results

    def _scan_channel(self, channel) -> ChannelScanResult:
        result = ChannelScanResult(channel_name=channel.name)
        try:
            recent = self._source.list_recent_videos(
                channel.youtube_channel_id, limit=self._scan_limit
            )
        except Exception as exc:  # noqa: BLE001 — un canal caído no frena a los demás
            logger.error("Error escaneando %s: %s", channel.name, exc)
            result.error = str(exc)
            return result

        if not recent:
            return result

        newest_id = recent[0].youtube_video_id

        if channel.last_video_id is None:
            self._channels.update_last_video(channel.id, newest_id)
            result.baseline_set = True
            logger.info("Línea base de %s: %s", channel.name, newest_id)
            return result

        for meta in recent:
            if meta.youtube_video_id == channel.last_video_id:
                break
            if self._videos.get_by_youtube_id(meta.youtube_video_id):
                continue
            video = self._videos.add(
                Video(
                    channel_id=channel.id,
                    youtube_video_id=meta.youtube_video_id,
                    title=meta.title,
                    duration_seconds=meta.duration_seconds,
                    published_at=meta.published_at,
                )
            )
            result.new_videos.append(video)
            logger.info("Video nuevo en %s: %s (%s)", channel.name, meta.title, meta.youtube_video_id)

        if newest_id != channel.last_video_id:
            self._channels.update_last_video(channel.id, newest_id)
        return result
