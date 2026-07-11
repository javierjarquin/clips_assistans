from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TranscriptSegment:
    """Segmento de transcripción con marcas de tiempo."""

    start_seconds: float
    end_seconds: float
    text: str


class InferenceEngine(ABC):
    """Motor de IA para transcripción. Adaptador por defecto: faster-whisper en CPU.

    El contrato admite un adaptador CUDA futuro sin cambiar a los consumidores.
    """

    @abstractmethod
    def transcribe(self, media_path: Path, language: str | None = None) -> list[TranscriptSegment]:
        """Transcribe el audio del archivo en segmentos con marcas de tiempo."""
