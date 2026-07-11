from dataclasses import dataclass
from datetime import datetime


@dataclass
class Channel:
    """Canal de YouTube monitoreado por el scanner."""

    youtube_channel_id: str
    name: str
    niche: str | None = None
    last_video_id: str | None = None
    active: bool = True
    id: int | None = None
    created_at: datetime | None = None
