from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    X = "x"


class PublicationStatus(str, Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class Publication:
    """Registro de publicación de un clip en una plataforma (tabla publish_log)."""

    clip_id: int
    platform: Platform
    status: PublicationStatus = PublicationStatus.PENDING
    post_url: str | None = None
    priority: int = 0
    retry_count: int = 0
    error_message: str | None = None
    published_at: datetime | None = None
    id: int | None = None
