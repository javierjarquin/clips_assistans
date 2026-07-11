"""Estrategia multi-API: intenta descargar con cada fuente en orden hasta que una funcione.

El listado (escaneo) usa solo la fuente primaria; los fallbacks aplican a la
descarga, que es donde YouTube endurece los controles.
"""

import logging
from pathlib import Path

from shorts_factory.ports.video_source import DownloadOutcome, VideoMetadata, VideoSourcePort

logger = logging.getLogger(__name__)


class FallbackVideoSource(VideoSourcePort):
    def __init__(self, sources: list[VideoSourcePort]) -> None:
        if not sources:
            raise ValueError("Se requiere al menos una fuente de video")
        self._sources = sources

    def list_recent_videos(self, youtube_channel_id: str, limit: int = 10) -> list[VideoMetadata]:
        return self._sources[0].list_recent_videos(youtube_channel_id, limit)

    def download(self, youtube_video_id: str, dest_path: Path) -> DownloadOutcome:
        errors: list[str] = []
        for source in self._sources:
            name = getattr(source, "name", type(source).__name__)
            outcome = source.download(youtube_video_id, dest_path)
            if outcome.success:
                return outcome
            logger.warning("Fuente %s falló para %s: %s", name, youtube_video_id, outcome.error)
            errors.append(f"{name}: {outcome.error}")
        return DownloadOutcome(
            success=False,
            method="fallback-agotado",
            error=" | ".join(errors),
        )
