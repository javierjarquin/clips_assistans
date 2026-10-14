"""Prueba real del recorte de colas de tts-kokoro con la voz de Fish 3.

    C:\\tts-kokoro\\.venv\\Scripts\\python.exe tools\\probar_recorte_colas.py
"""

import json
import os
import sys
from pathlib import Path

import soundfile as sf

sys.stdout.reconfigure(encoding="utf-8")
os.environ.update({"VOICESTUDIO_NUM_STEP": "32", "VOICESTUDIO_RECORTAR_COLAS": "1"})

from tts_kokoro.adapters.voicestudio_provider import VoiceStudioTTSProvider  # noqa: E402
from tts_kokoro.domain.text_normalizer import normalize_text  # noqa: E402

SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "colas" / "recorte"
SALIDA.mkdir(parents=True, exist_ok=True)
guion = json.loads(Path(r"C:\Android_in\guion-gisela-mota-temixco\guion.json").read_text(encoding="utf-8"))
prov = VoiceStudioTTSProvider()
for p in guion["planos"]:
    if p["id"] in ("p02", "p07"):
        r = prov.synthesize(normalize_text(p["narracion"]), voice="c1e4e1a4")
        sf.write(SALIDA / f"{p['id']}.wav", r.samples, r.sample_rate)
        print(p["id"], f"{len(r.samples) / r.sample_rate:.2f}s", flush=True)
