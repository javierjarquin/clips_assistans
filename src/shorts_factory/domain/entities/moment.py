from dataclasses import dataclass
from datetime import datetime


@dataclass
class Moment:
    """Segmento de reacción detectado por la IA, con puntaje de impacto y motivo."""

    video_id: int
    start_seconds: float
    end_seconds: float
    impact_score: float
    reason: str | None = None
    created_at: datetime | None = None
    id: int | None = None

    @property
    def duration_seconds(self) -> float:
        return self.end_seconds - self.start_seconds
