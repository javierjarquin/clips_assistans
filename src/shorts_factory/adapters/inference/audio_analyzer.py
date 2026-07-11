"""Análisis de audio con librosa: picos de volumen y ráfagas agudas (risas/gritos).

Señal v1: RMS normalizado (volumen) combinado con tasa de cruces por cero
(proxy de gritos/risas agudas). Se extrae la pista con ffmpeg a wav mono 16k
porque librosa no lee mp4 de forma confiable.
"""

import logging
import subprocess
import tempfile
from pathlib import Path

from shorts_factory.ports.analysis import AudioAnalyzerPort, AudioPeak

logger = logging.getLogger(__name__)


class LibrosaAudioAnalyzer(AudioAnalyzerPort):
    def __init__(self, ffmpeg_path: str = "ffmpeg", min_prominence: float = 0.1) -> None:
        self._ffmpeg = ffmpeg_path
        self._min_prominence = min_prominence

    def _extract_wav(self, media_path: Path, wav_path: Path) -> None:
        cmd = [
            self._ffmpeg, "-y", "-i", str(media_path),
            "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(wav_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg falló extrayendo audio: {result.stderr[-500:]}")

    def find_peaks(self, media_path: Path) -> list[AudioPeak]:
        import librosa
        import numpy as np
        from scipy.signal import find_peaks

        with tempfile.TemporaryDirectory() as tmp:
            wav_path = Path(tmp) / "audio.wav"
            self._extract_wav(media_path, wav_path)
            y, sr = librosa.load(str(wav_path), sr=16000, mono=True)

        hop = 512
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop)[0]
        times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop)

        def normalize(x):
            rng = x.max() - x.min()
            return (x - x.min()) / rng if rng > 0 else np.zeros_like(x)

        # 70% volumen + 30% agudeza: sube risas/gritos frente a voz plana
        intensity = 0.7 * normalize(rms) + 0.3 * normalize(zcr)

        idx, _ = find_peaks(intensity, prominence=self._min_prominence, distance=sr // hop)
        peaks = [
            AudioPeak(time_seconds=float(times[i]), intensity=float(intensity[i])) for i in idx
        ]
        logger.info("Audio de %s: %d picos detectados", media_path.name, len(peaks))
        return peaks
