"""Puertos de las señales complementarias del análisis: audio y escenas."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioPeak:
    """Pico de intensidad de audio (volumen/risa/grito) con intensidad normalizada 0-1."""

    time_seconds: float
    intensity: float


class AudioAnalyzerPort(ABC):
    @abstractmethod
    def find_peaks(self, media_path: Path) -> list[AudioPeak]:
        """Detecta picos de intensidad en la pista de audio."""


class SceneDetectorPort(ABC):
    @abstractmethod
    def detect_scene_changes(self, media_path: Path) -> list[float]:
        """Marca de tiempo (segundos) de cada cambio brusco de plano."""
