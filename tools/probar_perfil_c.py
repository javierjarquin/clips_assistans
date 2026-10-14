"""Perfil C de Fish 3 (referencia cortada justo al final de la palabra, sin la
respiración de la muestra) contra Fish 2 (muestra limpia), con el ajuste B.

    .venv\\Scripts\\python.exe tools\\probar_perfil_c.py
"""

import json
from pathlib import Path

import requests

SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "colas" / "perfil_c"
SALIDA.mkdir(parents=True, exist_ok=True)
guion = json.loads(Path(r"C:\Android_in\guion-gisela-mota-temixco\guion.json").read_text(encoding="utf-8"))
textos = {p["id"]: p["narracion"] for p in guion["planos"] if p["id"] in ("p02", "p07")}
for nombre, voz, pid in [("C", "37a82ee9", "p07"), ("C", "37a82ee9", "p02"),
                         ("fish2", "746b6e2d", "p07")]:
    wav = SALIDA / f"{nombre}_{pid}.wav"
    if wav.exists():
        continue
    r = requests.post("http://localhost:3900/v1/audio/speech", timeout=1800, json={
        "model": "omnivoice", "voice": voz, "input": textos[pid], "response_format": "wav",
        "num_step": 32})
    r.raise_for_status()
    wav.write_bytes(r.content)
    print("listo", wav.name, flush=True)
