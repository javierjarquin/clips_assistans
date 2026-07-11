from abc import ABC, abstractmethod
from pathlib import Path


class VideoProcessorPort(ABC):
    """Manipulación de archivos de video. Adaptador inicial: FFmpeg por CLI."""

    @abstractmethod
    def cut_segment(
        self, source: Path, start_seconds: float, end_seconds: float, dest: Path
    ) -> Path:
        """Corta un segmento del video por marcas de tiempo y lo guarda en dest."""

    @abstractmethod
    def to_vertical(self, source: Path, dest: Path) -> Path:
        """Convierte el video a formato vertical 9:16 (recorte centrado o fondo desenfocado)."""

    def cut_vertical(
        self, source: Path, start_seconds: float, end_seconds: float, dest: Path
    ) -> Path:
        """Corta y convierte a 9:16. Los adaptadores pueden hacerlo en una sola pasada."""
        temp = dest.with_suffix(".tmp.mp4")
        self.cut_segment(source, start_seconds, end_seconds, temp)
        try:
            return self.to_vertical(temp, dest)
        finally:
            temp.unlink(missing_ok=True)
