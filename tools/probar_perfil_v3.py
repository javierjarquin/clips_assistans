"""Prueba del perfil v3 de Fish 3 (muestra nueva, pausa limpia) con los planos
de Gisela Mota que fallaron: p01 ("…era del PRD"), p03 ("Gustavo Villa
Mejía"), p04 ("municipales") y p07 (el cierre). Plano entero, sin recorte:
así sale la voz tal cual. Deja un mp3 para escuchar.

    .venv\\Scripts\\python.exe tools\\probar_perfil_v3.py
"""

import json
import subprocess
import sys
from pathlib import Path

import requests
from faster_whisper import WhisperModel

sys.path.insert(0, r"C:\tts-kokoro\src")
from tts_kokoro.domain.text_normalizer import normalize_text  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "voz_fish3_v3" / "prueba"
SALIDA.mkdir(parents=True, exist_ok=True)
guion = json.loads(Path(r"C:\Android_in\guion-gisela-mota-temixco\guion.json").read_text(encoding="utf-8"))
planos = [p for p in guion["planos"] if p["id"] in ("p01", "p03", "p04", "p07")]
modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")

for p in planos:
    wav = SALIDA / f"{p['id']}.wav"
    if not wav.exists():
        r = requests.post("http://localhost:3900/v1/audio/speech", timeout=1800, json={
            "model": "omnivoice", "voice": "cbbc2aa7", "input": normalize_text(p["narracion"]),
            "response_format": "wav", "num_step": 32})
        r.raise_for_status()
        wav.write_bytes(r.content)
    oido = " ".join(s.text.strip() for s in modelo.transcribe(str(wav), language="es",
                                                              vad_filter=True)[0])
    print(f"{p['id']}\n  guion: {p['narracion']}\n  oído:  {oido}", flush=True)

lista = SALIDA / "_lista.txt"
silencio = SALIDA / "_silencio.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                "anullsrc=r=24000:cl=mono", "-t", "1.2", str(silencio)], check=True)
lineas = []
for p in planos:
    lineas += [f"file '{(SALIDA / (p['id'] + '.wav')).as_posix()}'", f"file '{silencio.as_posix()}'"]
lista.write_text("\n".join(lineas), encoding="utf-8")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
                "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k",
                str(SALIDA / "prueba_fish3_v3.mp3")], check=True)
