"""Revisa y arma la evidencia de varios guiones (sin Claude), y deja una hoja
con todas las piezas de cada uno para revisarlas a ojo.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\preparar_guiones.py slug1 slug2 ...
"""

import json
import logging
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, r"C:\dato-mata-gato-bot\src")
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.WARNING)

from dato_mata_gato_bot import evidencia, revision_guion  # noqa: E402

for slug in sys.argv[1:]:
    base = Path(r"C:\Android_in") / slug
    g = json.loads((base / "guion.json").read_text(encoding="utf-8-sig"))
    print(f"\n== {slug}: {sum(len(p['narracion'].split()) for p in g['planos'])} palabras")
    print("   revisión:", revision_guion.problemas(g) or "OK")
    rep = evidencia.preparar(slug)
    print("  ", rep.resumen(), rep.fallidas or "")
    m = json.loads((base / "evidencia" / "manifest.json").read_text(encoding="utf-8-sig"))
    for pid, v in m.items():
        if v.get("titular"):
            print(f"   {pid}: {v['titular'][:100]}")
    piezas = sorted((base / "evidencia").glob("*.jpg"))
    hoja = Image.new("RGB", (180 * len(piezas), 320), (20, 20, 20))
    for i, p in enumerate(piezas):
        im = Image.open(p).convert("RGB")
        im.thumbnail((180, 320))
        hoja.paste(im, (i * 180 + (180 - im.width) // 2, (320 - im.height) // 2))
    hoja.save(base / "evidencia" / "_hoja.jpg", quality=85)
