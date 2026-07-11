from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class VideoMetadata:
    """Metadatos de un video listado sin descargar (modo flat-playlist)."""

    youtube_video_id: str
    title: str
    duration_seconds: int | None = None
    published_at: datetime | None = None


@dataclass(frozen=True)
class DownloadOutcome:
    """Resultado de un intento de descarga."""

    success: bool
    file_path: Path | None = None
    size_bytes: int | None = None
    method: str | None = None
    error: str | None = None


class VideoSourcePort(ABC):
    """Fuente de videos: listar recientes de un canal y descargar uno concreto."""

    @abstractmethod
    def list_recent_videos(self, youtube_channel_id: str, limit: int = 10) -> list[VideoMetadata]:
        """Lista los videos más recientes del canal, solo metadatos, del más nuevo al más viejo."""

    @abstractmethod
    def download(self, youtube_video_id: str, dest_path: Path) -> DownloadOutcome:
        """Descarga el video completo a la ruta indicada."""
