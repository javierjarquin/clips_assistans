"""¿De dónde sale el "cia" de Fish 3? Compara el perfil actual contra dos
perfiles nuevos con la referencia limpia, sobre las frases que salieron mal en
el lote /lotefish3 del 29/09/2026 (Gisela Mota).

Para cada síntesis mide: qué entiende Whisper, y la energía que queda en cada
hueco después de un punto (entre frases y al final). Si el perfil arrastra el
final de su referencia ("experien-CIA"), esos huecos tienen voz.

    .venv\\Scripts\\python.exe tools\\comparar_perfiles_fish3.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import requests
import soundfile as sf
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "colas" / "perfiles"
SALIDA.mkdir(parents=True, exist_ok=True)
PERFILES = {"actual": "81f929e4", "A_frase1": "c1e4e1a4", "B_completa_pad": "fac868f2"}
guion = json.loads(Path(r"C:\Android_in\guion-gisela-mota-temixco\guion.json").read_text(encoding="utf-8"))
TEXTOS = {p["id"]: p["narracion"] for p in guion["planos"] if p["id"] in ("p02", "p07")}

modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
resumen = {}
for nombre, perfil in PERFILES.items():
    for pid, texto in TEXTOS.items():
        wav = SALIDA / f"{nombre}_{pid}.wav"
        if not wav.exists():
            r = requests.post("http://localhost:3900/v1/audio/speech", timeout=1800, json={
                "model": "omnivoice", "voice": perfil, "input": texto,
                "response_format": "wav", "num_step": 32})
            r.raise_for_status()
            wav.write_bytes(r.content)
        audio, sr = sf.read(wav, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        palabras = [w for s in modelo.transcribe(str(wav), language="es", word_timestamps=True,
                                                 vad_filter=False)[0] for w in s.words]
        oido = "".join(w.word for w in palabras).strip()
        # Huecos tras cada palabra que termina en punto/signo, y la cola final.
        huecos = []
        for i, w in enumerate(palabras):
            if re.search(r"[.?!]$", w.word.strip()):
                fin = w.end
                sig = palabras[i + 1].start if i + 1 < len(palabras) else len(audio) / sr
                tramo = audio[int(fin * sr):int(sig * sr)]
                if len(tramo):
                    huecos.append(round(float(np.sqrt(np.mean(tramo ** 2))), 3))
        resumen.setdefault(nombre, []).extend(huecos)
        print(f"{nombre:15} {pid}: oído {oido!r}\n{'':19}energía en los huecos tras punto: {huecos}",
              flush=True)

print()
for nombre, h in resumen.items():
    print(f"{nombre:15} energía media tras punto: {np.mean(h):.3f}")

# Para escuchar: los tres perfiles seguidos, con un bip entre uno y otro.
lista = SALIDA / "_lista.txt"
bip = SALIDA / "_bip.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                "sine=frequency=880:duration=0.25", "-ar", "24000", "-ac", "1", str(bip)], check=True)
lineas = []
for nombre in PERFILES:
    for pid in TEXTOS:
        lineas += [f"file '{bip.as_posix()}'", f"file '{(SALIDA / f'{nombre}_{pid}.wav').as_posix()}'"]
lista.write_text("\n".join(lineas), encoding="utf-8")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
                "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k",
                str(SALIDA / "comparar_perfiles_fish3.mp3")], check=True)
