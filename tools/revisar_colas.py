"""¿La voz agrega algo al final de cada frase? Mide la "cola" de cada plano:
lo que suena DESPUÉS de la última palabra que Whisper reconoce, y transcribe
ese pedazo solo.

    .venv\\Scripts\\python.exe tools\\revisar_colas.py <slug>

Nace del lote /lotefish3 del 29/09/2026: el usuario oía "cia" al final de
cada frase. Whisper, sobre el plano entero, no lo escribe (descarta sílabas
sueltas), así que hay que aislar la cola.
"""

import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
slug = sys.argv[1]
carpeta = Path(r"C:\tts-kokoro\projects") / slug / "narracion"
salida = Path(__file__).resolve().parents[1] / "analisis" / "colas" / slug
salida.mkdir(parents=True, exist_ok=True)
modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")

for wav in sorted(carpeta.glob("p*.wav")):
    audio, sr = sf.read(wav, dtype="float32")
    dur = len(audio) / sr
    segs, _ = modelo.transcribe(str(wav), language="es", word_timestamps=True, vad_filter=False)
    palabras = [w for s in segs for w in s.words]
    if not palabras:
        continue
    fin = palabras[-1].end
    cola = audio[int(fin * sr):]
    rms = float(np.sqrt(np.mean(cola ** 2))) if len(cola) else 0.0
    oido = ""
    if len(cola) > sr * 0.15 and rms > 0.01:
        ruta = salida / f"{wav.stem}_cola.wav"
        # Un poco antes del final, para que Whisper tenga de dónde agarrarse.
        sf.write(ruta, audio[int(max(0, fin - 0.6) * sr):], sr)
        oido = " ".join(s.text.strip() for s in modelo.transcribe(
            str(ruta), language="es", vad_filter=False)[0])
    print(f"{wav.stem}: última palabra {palabras[-1].word.strip()!r} termina {fin:.2f}s "
          f"de {dur:.2f}s | cola {dur - fin:.2f}s rms {rms:.3f} | cola dice: {oido!r}",
          flush=True)
