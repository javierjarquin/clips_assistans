"""Energía cada 20 ms en los bordes de un audio, contra dónde empieza la
primera palabra y termina la última según Whisper. Para encontrar sonidos
fuera de las palabras (el "cia" de Fish 3).

    .venv\\Scripts\\python.exe tools\\envolvente_bordes.py archivo.wav [...]
"""

import sys

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
PASO = 0.02


def barras(env):
    return "".join(" ▁▂▃▄▅▆▇█"[min(8, int(e / 0.02))] for e in env)


for ruta in sys.argv[1:]:
    audio, sr = sf.read(ruta, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    n = int(PASO * sr)
    env = [float(np.sqrt(np.mean(audio[i:i + n] ** 2))) for i in range(0, len(audio) - n, n)]
    palabras = [w for s in modelo.transcribe(ruta, language="es", word_timestamps=True,
                                             vad_filter=False)[0] for w in s.words]
    ini, fin, dur = palabras[0].start, palabras[-1].end, len(audio) / sr
    print(f"\n{ruta.split(chr(92))[-1]}  ({dur:.2f}s)  primera palabra {palabras[0].word.strip()!r} "
          f"@{ini:.2f}s  última {palabras[-1].word.strip()!r} termina @{fin:.2f}s")
    a = int(max(0, ini - 0.1) / PASO)
    print(f"  inicio 0.00-{ini + 0.3:.2f}s: {barras(env[:int((ini + 0.3) / PASO)])}")
    print(f"  final  {fin - 0.4:.2f}-{dur:.2f}s: {barras(env[int((fin - 0.4) / PASO):])}")
    print(f"         (la última palabra termina en la posición {int(0.4 / PASO)} de esa barra)")
    # Huecos entre frases: después de cada palabra con punto.
    for i, w in enumerate(palabras[:-1]):
        if w.word.strip()[-1:] in ".?!":
            s, e = w.end, palabras[i + 1].start
            print(f"  hueco tras {w.word.strip()!r} {s:.2f}-{e:.2f}s: "
                  f"{barras(env[int((s - 0.1) / PASO):int((e + 0.1) / PASO)])}")
