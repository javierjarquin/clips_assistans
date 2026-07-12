"""Clips listos para el panel de publicación manual: qué se puede publicar,
dónde ya se publicó, y si conviene esperar según el ritmo sugerido (1/día).
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from shorts_factory.domain.entities.clip import ClipStatus
from shorts_factory.domain.entities.publication import PublicationStatus
from shorts_factory.ports.repository import (
    ChannelRepository,
    ClipRepository,
    MomentRepository,
    PublishLogRepository,
    VideoRepository,
)

_SUGGESTED_INTERVAL_HOURS = 24


@dataclass(frozen=True)
class PublishableClip:
    clip_id: int
    video_title: str
    channel_name: str
    duration_seconds: float | None
    impact_score: float | None
    reason: str | None
    file_exists: bool
    published_on: frozenset[str] = field(default_factory=frozenset)  # platforms ya publicadas

    @property
    def publishable(self) -> bool:
        return self.file_exists


class ListPublishableClips:
    def __init__(
        self,
        clip_repo: ClipRepository,
        moment_repo: MomentRepository,
        video_repo: VideoRepository,
        channel_repo: ChannelRepository,
        publish_log_repo: PublishLogRepository,
    ) -> None:
        self._clips = clip_repo
        self._moments = moment_repo
        self._videos = video_repo
        self._channels = channel_repo
        self._log = publish_log_repo

    def execute(self) -> list[PublishableClip]:
        result = []
        for clip in self._clips.list_by_status(ClipStatus.READY):
            moment = self._moments.get(clip.moment_id)
            video = self._videos.get(moment.video_id) if moment else None
            channel = self._channels.get(video.channel_id) if video else None
            published_on = frozenset(
                p.platform.value
                for p in self._log.list_by_clip(clip.id)
                if p.status == PublicationStatus.PUBLISHED
            )
            result.append(
                PublishableClip(
                    clip_id=clip.id,
                    video_title=video.title if video else "(video desconocido)",
                    channel_name=channel.name if channel else "(canal desconocido)",
                    duration_seconds=clip.duration_seconds,
                    impact_score=moment.impact_score if moment else None,
                    reason=moment.reason if moment else None,
                    file_exists=bool(clip.file_path and Path(clip.file_path).exists()),
                    published_on=published_on,
                )
            )
        return result

    def last_published_at(self) -> datetime | None:
        dates = [
            p.published_at
            for p in self._log.list_by_status(PublicationStatus.PUBLISHED)
            if p.published_at
        ]
        return max(dates, default=None)

    def should_suggest_waiting(self, now: datetime | None = None) -> bool:
        """True si ya se publicó algo dentro de la ventana sugerida (~24h)."""
        last = self.last_published_at()
        if last is None:
            return False
        now = now or datetime.now()
        return (now - last).total_seconds() < _SUGGESTED_INTERVAL_HOURS * 3600
