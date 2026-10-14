"""¿El golpe de sonido después de cada frase ("cia") lo pone la voz de Fish 3
o el ajuste B (num_step=32)? Misma frase, cuatro combinaciones.

    .venv\\Scripts\\python.exe tools\\aislar_cia.py
"""

import json
from pathlib import Path

import requests

SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "colas" / "aislar"
SALIDA.mkdir(parents=True, exist_ok=True)
guion = json.loads(Path(r"C:\Android_in\guion-gisela-mota-temixco\guion.json").read_text(encoding="utf-8"))
texto = next(p["narracion"] for p in guion["planos"] if p["id"] == "p07")

for nombre, voz, pasos in [("fish3A_16", "c1e4e1a4", 16), ("javier_32", "95e2570b", 32),
                           ("javier_16", "95e2570b", 16), ("fish3A_32b", "c1e4e1a4", 32)]:
    wav = SALIDA / f"{nombre}.wav"
    if wav.exists():
        continue
    r = requests.post("http://localhost:3900/v1/audio/speech", timeout=1800, json={
        "model": "omnivoice", "voice": voz, "input": texto, "response_format": "wav",
        "num_step": pasos})
    r.raise_for_status()
    wav.write_bytes(r.content)
    print("listo", nombre, flush=True)
