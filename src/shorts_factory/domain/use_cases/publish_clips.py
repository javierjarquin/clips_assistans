"""Cola de publicación priorizada.

Encola cada clip listo una vez por plataforma habilitada (prioridad configurable)
y procesa pendientes en orden de prioridad. Un fallo reintenta hasta el límite
con el contador en publish_log; un fallo en una red no bloquea a las demás.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from shorts_factory.domain.entities.clip import ClipStatus
from shorts_factory.domain.entities.publication import (
    Platform,
    Publication,
    PublicationStatus,
)
from shorts_factory.ports.publisher import PublisherPort
from shorts_factory.ports.repository import (
    ClipRepository,
    MomentRepository,
    PublishLogRepository,
    VideoRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class PublishReport:
    published: list[Publication] = field(default_factory=list)
    failed: list[Publication] = field(default_factory=list)
    enqueued: int = 0


class PublishClips:
    def __init__(
        self,
        clip_repo: ClipRepository,
        moment_repo: MomentRepository,
        video_repo: VideoRepository,
        publish_log_repo: PublishLogRepository,
        publishers: dict[Platform, PublisherPort],
        priorities: dict[Platform, int] | None = None,
        max_retries: int = 3,
    ) -> None:
        self._clips = clip_repo
        self._moments = moment_repo
        self._videos = video_repo
        self._log = publish_log_repo
        self._publishers = publishers
        self._priorities = priorities or {}
        self._max_retries = max_retries

    def execute(self, clip_id: int | None = None) -> PublishReport:
        """clip_id restringe la corrida a un solo clip (panel de publicación manual).

        Sin clip_id, procesa todos los clips listos (uso desatendido/CLI).
        """
        report = PublishReport()
        self._enqueue_ready_clips(report, clip_id)
        self._process_pending(report, clip_id)
        return report

    def _enqueue_ready_clips(self, report: PublishReport, clip_id: int | None) -> None:
        for clip in self._clips.list_by_status(ClipStatus.READY):
            if clip_id is not None and clip.id != clip_id:
                continue
            existing = {p.platform for p in self._log.list_by_clip(clip.id)}
            for platform in self._publishers:
                if platform in existing:
                    continue
                self._log.add(
                    Publication(
                        clip_id=clip.id,
                        platform=platform,
                        priority=self._priorities.get(platform, 0),
                    )
                )
                report.enqueued += 1

    def _process_pending(self, report: PublishReport, clip_id: int | None) -> None:
        for publication in self._log.list_by_status(PublicationStatus.PENDING):
            if clip_id is not None and publication.clip_id != clip_id:
                continue
            publisher = self._publishers.get(publication.platform)
            if publisher is None:
                continue
            clip = self._clips.get(publication.clip_id)
            if clip is None or not clip.file_path or not Path(clip.file_path).exists():
                publication.status = PublicationStatus.FAILED
                publication.error_message = "archivo del clip no existe"
                self._log.update(publication)
                report.failed.append(publication)
                continue

            publication.status = PublicationStatus.PUBLISHING
            self._log.update(publication)
            try:
                outcome = publisher.publish(Path(clip.file_path), self._caption_for(clip))
            except Exception as exc:  # noqa: BLE001 — el adaptador no debe tumbar la cola
                outcome = None
                error = str(exc)
            else:
                error = outcome.error or "publicación fallida"

            if outcome and outcome.success:
                publication.status = PublicationStatus.PUBLISHED
                publication.post_url = outcome.post_url
                publication.published_at = datetime.now()
                publication.error_message = None
                report.published.append(publication)
                logger.info(
                    "Publicado clip %d en %s: %s",
                    clip.id,
                    publication.platform.value,
                    outcome.post_url,
                )
            else:
                publication.retry_count += 1
                exhausted = publication.retry_count >= self._max_retries
                publication.status = (
                    PublicationStatus.FAILED if exhausted else PublicationStatus.PENDING
                )
                publication.error_message = error
                report.failed.append(publication)
                logger.error(
                    "Fallo publicando clip %d en %s (intento %d/%d): %s",
                    clip.id,
                    publication.platform.value,
                    publication.retry_count,
                    self._max_retries,
                    error,
                )
            self._log.update(publication)

    def _caption_for(self, clip) -> str:
        moment = self._moments.get(clip.moment_id)
        if moment:
            video = self._videos.get(moment.video_id)
            if video:
                return video.title
        return "Nuevo clip"
