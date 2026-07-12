"""Encola el video más reciente de un canal para descarga inmediata.

ScanChannels nunca hace esto a propósito: el primer escaneo solo fija línea
base para no inundar el pipeline con contenido viejo al agregar un canal en
producción. Pero para probar el sistema con un canal nuevo, sin esperar a que
publique algo, hace falta una vía explícita — esta.
"""

from shorts_factory.domain.entities.video import Video
from shorts_factory.ports.repository import ChannelRepository, VideoRepository
from shorts_factory.ports.video_source import VideoSourcePort


class ChannelNotFoundError(Exception):
    pass


class BootstrapChannelWithLatestVideo:
    def __init__(
        self,
        channel_repo: ChannelRepository,
        video_repo: VideoRepository,
        video_source: VideoSourcePort,
    ) -> None:
        self._channels = channel_repo
        self._videos = video_repo
        self._source = video_source

    def execute(self, channel_id: int) -> Video | None:
        """Devuelve el video encolado, o None si el canal no tiene videos públicos."""
        channel = self._channels.get(channel_id)
        if channel is None:
            raise ChannelNotFoundError(f"No existe el canal #{channel_id}")

        recent = self._source.list_recent_videos(channel.youtube_channel_id, limit=1)
        if not recent:
            return None
        meta = recent[0]

        self._channels.update_last_video(channel.id, meta.youtube_video_id)
        existing = self._videos.get_by_youtube_id(meta.youtube_video_id)
        if existing:
            return existing
        return self._videos.add(
            Video(
                channel_id=channel.id,
                youtube_video_id=meta.youtube_video_id,
                title=meta.title,
                duration_seconds=meta.duration_seconds,
                published_at=meta.published_at,
            )
        )
