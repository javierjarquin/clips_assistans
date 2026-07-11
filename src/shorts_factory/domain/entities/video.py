from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    """Estados del video a lo largo del pipeline (ver 03-Analisis-Tecnico §5)."""

    DETECTED = "detected"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    DONE = "done"
    ERROR = "error"


@dataclass
class Video:
    """Video detectado en un canal, viaja por el pipeline según su estado."""

    channel_id: int
    youtube_video_id: str
    title: str
    duration_seconds: int | None = None
    published_at: datetime | None = None
    status: VideoStatus = VideoStatus.DETECTED
    detected_at: datetime | None = None
    id: int | None = None
