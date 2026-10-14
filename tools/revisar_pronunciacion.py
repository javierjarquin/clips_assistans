"""¿Qué palabras pronunció mal la voz? Transcribe cada plano con Whisper y lo
compara palabra por palabra con el guion.

    .venv\\Scripts\\python.exe tools\\revisar_pronunciacion.py <slug>

Whisper no es perfecto: una diferencia es un candidato para ESCUCHAR, no una
prueba. Pero una palabra que Whisper no reconoce casi siempre es una que la
voz dijo raro (nombres propios, siglas, marcas, números).
"""

import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
slug = sys.argv[1]
guion = json.loads((Path(r"C:\Android_in") / slug / "guion.json").read_text(encoding="utf-8"))
wavs = Path(r"C:\tts-kokoro\projects") / slug / "narracion"


def norm(t: str) -> list[str]:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9ñ]+", t)


modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
reporte = []
for plano in guion["planos"]:
    wav = wavs / f"{plano['id']}.wav"
    if not wav.exists():
        continue
    segs, _ = modelo.transcribe(str(wav), language="es", vad_filter=False,
                                initial_prompt=None, beam_size=5)
    oido = " ".join(s.text.strip() for s in segs)
    esperado, escuchado = norm(plano["narracion"]), norm(oido)
    difs = []
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(None, esperado, escuchado).get_opcodes():
        if op != "equal":
            difs.append((" ".join(esperado[a1:a2]), " ".join(escuchado[b1:b2])))
    reporte.append({"plano": plano["id"], "oido": oido, "diferencias": difs})
    print(f"\n[{plano['id']}] {oido}")
    for guion_dice, voz_dice in difs:
        print(f"   guion: {guion_dice!r:40} voz: {voz_dice!r}")
Path(__file__).resolve().parents[1].joinpath("analisis", f"pronunciacion_{slug}.json").write_text(
    json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
