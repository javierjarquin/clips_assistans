from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ClipStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


@dataclass
class Clip:
    """Archivo ya cortado en formato vertical, listo para publicar."""

    moment_id: int
    file_path: str | None = None
    duration_seconds: float | None = None
    format: str = "9:16"
    status: ClipStatus = ClipStatus.PENDING
    created_at: datetime | None = None
    id: int | None = None
