from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from shorts_factory.domain.entities.publication import Platform


@dataclass(frozen=True)
class PublishOutcome:
    """Resultado de un intento de publicación."""

    success: bool
    post_url: str | None = None
    error: str | None = None


class PublisherPort(ABC):
    """Publicación de un clip en una red social. Un adaptador por plataforma."""

    @property
    @abstractmethod
    def platform(self) -> Platform:
        """Plataforma que implementa este adaptador."""

    @abstractmethod
    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        """Publica el clip con el texto dado y devuelve URL o error."""
