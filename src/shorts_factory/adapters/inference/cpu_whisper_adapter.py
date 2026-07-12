"""Transcripción con faster-whisper en CPU (CTranslate2, int8, multihilo).

El modelo se carga perezosamente en la primera transcripción: importar este
módulo no arrastra las librerías de ML.
"""

import logging
from pathlib import Path

from shorts_factory.ports.inference_engine import InferenceEngine, TranscriptSegment

logger = logging.getLogger(__name__)


class FasterWhisperEngine(InferenceEngine):
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        cpu_threads: int = 0,
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._cpu_threads = cpu_threads
        self._model = None

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info(
                "Cargando modelo whisper '%s' (%s, %s)",
                self._model_size,
                self._device,
                self._compute_type,
            )
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
                cpu_threads=self._cpu_threads,
            )
        return self._model

    def transcribe(self, media_path: Path, language: str | None = None) -> list[TranscriptSegment]:
        model = self._load_model()
        segments, info = model.transcribe(str(media_path), language=language, vad_filter=True)
        logger.info(
            "Transcribiendo %s (~%.0fs de audio, %s)…",
            media_path.name, info.duration, language or "detectando idioma",
        )
        result: list[TranscriptSegment] = []
        last_logged = 0.0
        for s in segments:
            result.append(
                TranscriptSegment(
                    start_seconds=float(s.start), end_seconds=float(s.end), text=s.text.strip()
                )
            )
            # Progreso cada ~30s de audio procesado: con cientos de segmentos por
            # video, loguear uno por uno inundaría el log sin aportar señal.
            if s.end - last_logged >= 30:
                logger.info(
                    "  %s: %.0fs / %.0fs transcritos", media_path.name, s.end, info.duration
                )
                last_logged = s.end
        logger.info(
            "Transcrito %s: %d segmentos, idioma %s", media_path.name, len(result), info.language
        )
        return result
