"""Resumen final de una fábrica, para Telegram (12/10/2026).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\resumen_fabrica.py piloto-cercania
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

lote = sys.argv[1]
e = json.load(open(Path(r"C:\Android_in\fabrica") / lote / "estado.json", encoding="utf-8"))
lineas = [f"PILOTO TERMINADO ({e['lote']})", ""]
for slug, v in e["videos"].items():
    try:
        g = json.load(open(Path(r"C:\Android_in") / slug / "guion.json", encoding="utf-8"))
        titulo, voz = g.get("titulo", slug), g.get("voz_narrador", "?")
    except (OSError, ValueError):
        titulo, voz = slug, "?"
    marca = {"listo": "OK", "fallido": "FALLÓ"}.get(v["estado"], "PENDIENTE")
    lineas.append(f"{marca} [{slug.split('-')[1]}] {titulo} | voz: {'tu voz' if voz == 'javier' else 'Fish 3'}")
tot = sum(c.get("total", 0) for c in e.get("consumo", []))
g = sum(c.get("guiones", 0) for c in e.get("consumo", []))
lineas += ["", f"Claude: {tot / 1e6:.0f} M tokens en {g} guiones aceptados",
           f"Videos en: {e['carpeta_videos']}", "",
           r"Si te gustan, los 1000 se lanzan con: tools\fabrica.py crear mil-1 1000",
           "La PC se apaga en 5 minutos. Para cancelar: shutdown /a"]
print("\n".join(lineas))
