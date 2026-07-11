from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DownloadStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Download:
    """Evento de descarga de un video; puede fallar y reintentarse."""

    video_id: int
    file_path: str | None = None
    size_bytes: int | None = None
    method: str | None = None
    status: DownloadStatus = DownloadStatus.PENDING
    error_message: str | None = None
    completed_at: datetime | None = None
    id: int | None = None
