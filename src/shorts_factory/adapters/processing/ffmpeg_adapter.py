"""Adaptador FFmpeg: corte por marcas de tiempo y conversión a vertical 9:16.

Encoder "auto": usa h264_amf (GPU AMD vía AMF, independiente de ROCm) si el
build de ffmpeg lo trae; si no, cae a libx264 por CPU.
"""

import logging
import subprocess
from pathlib import Path

from shorts_factory.ports.video_processor import VideoProcessorPort

logger = logging.getLogger(__name__)

# 9:16 sin recortar contenido: el cuadro completo se escala para caber (contain)
# sobre un fondo del mismo video, ampliado a cubrir el lienzo y difuminado. Un
# crop central puro descartaría ~68% del ancho en fuentes 16:9 — suficiente para
# cortar títulos, subtítulos incrustados o pantallas compartidas por los bordes.
_VERTICAL_FILTER_COMPLEX = (
    "[0:v]split=2[bg][fg];"
    "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,gblur=sigma=20,eq=brightness=-0.1[bg];"
    "[fg]scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=ceil(iw/2)*2:ceil(ih/2)*2[fg];"
    "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[vout]"
)


class FFmpegProcessor(VideoProcessorPort):
    def __init__(self, ffmpeg_path: str = "ffmpeg", encoder: str = "auto") -> None:
        self._ffmpeg = ffmpeg_path
        self._encoder = encoder
        self._resolved_encoder: str | None = None

    def _run(self, args: list[str]) -> None:
        cmd = [self._ffmpeg, "-hide_banner", "-y", *args]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg falló ({result.returncode}): {result.stderr[-800:]}")

    def _run_encode(self, pre_args: list[str], post_args: list[str]) -> None:
        """Ejecuta un encode; si el encoder por hardware falla, reintenta con libx264."""
        try:
            self._run([*pre_args, *self._encode_args(), *post_args])
        except RuntimeError:
            if self._pick_encoder() == "libx264":
                raise
            logger.warning("Encoder %s falló; reintentando con libx264", self._resolved_encoder)
            self._resolved_encoder = "libx264"
            self._run([*pre_args, *self._encode_args(), *post_args])

    def _pick_encoder(self) -> str:
        """Prueba funcional de encoders por hardware; el que codifica de verdad, gana.

        Listar encoders no basta: el build puede traer h264_amf compilado pero
        sin runtime AMD en la máquina (o nvenc sin GPU NVIDIA). Se codifica un
        frame de prueba con cada candidato: PC de casa -> AMF, laptop -> NVENC.
        """
        if self._resolved_encoder:
            return self._resolved_encoder
        if self._encoder != "auto":
            self._resolved_encoder = self._encoder
            return self._encoder
        for candidate in ("h264_nvenc", "h264_amf", "h264_qsv"):
            probe = subprocess.run(
                [
                    self._ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-i", "testsrc2=duration=0.1:size=256x256:rate=30",
                    "-frames:v", "1", "-c:v", candidate, "-f", "null", "-",
                ],
                capture_output=True,
                text=True,
            )
            if probe.returncode == 0:
                logger.info("Encoder de video: %s (hardware)", candidate)
                self._resolved_encoder = candidate
                return candidate
        logger.info("Encoder de video: libx264 (CPU)")
        self._resolved_encoder = "libx264"
        return "libx264"

    def _encode_args(self) -> list[str]:
        encoder = self._pick_encoder()
        args = ["-c:v", encoder, "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"]
        if encoder == "libx264":
            args += ["-preset", "veryfast", "-crf", "23"]
        else:
            args += ["-b:v", "6M"]
        return args

    def cut_segment(
        self, source: Path, start_seconds: float, end_seconds: float, dest: Path
    ) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        # -ss antes de -i: seek rápido; re-encode para corte preciso sin esperar keyframe
        self._run_encode(
            ["-ss", f"{start_seconds:.3f}", "-to", f"{end_seconds:.3f}", "-i", str(source)],
            [str(dest)],
        )
        return dest

    def to_vertical(self, source: Path, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        self._run_encode(
            [
                "-i", str(source),
                "-filter_complex", _VERTICAL_FILTER_COMPLEX,
                "-map", "[vout]", "-map", "0:a?",
            ],
            [str(dest)],
        )
        return dest

    def cut_vertical(
        self, source: Path, start_seconds: float, end_seconds: float, dest: Path
    ) -> Path:
        """Corte + vertical en una sola pasada de encode."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        self._run_encode(
            [
                "-ss", f"{start_seconds:.3f}", "-to", f"{end_seconds:.3f}", "-i", str(source),
                "-filter_complex", _VERTICAL_FILTER_COMPLEX,
                "-map", "[vout]", "-map", "0:a?",
            ],
            [str(dest)],
        )
        return dest

    def probe_duration(self, source: Path) -> float | None:
        """Duración en segundos vía ffprobe (junto a ffmpeg en el mismo build)."""
        ffprobe = str(Path(self._ffmpeg).parent / "ffprobe") if "\\" in self._ffmpeg or "/" in self._ffmpeg else "ffprobe"
        result = subprocess.run(
            [
                ffprobe, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(source),
            ],
            capture_output=True,
            text=True,
        )
        try:
            return float(result.stdout.strip())
        except ValueError:
            return None
