"""Cuántos tokens gastó Claude escribiendo cada lote de guiones del bot (12/10/2026).

Recorre las sesiones del bot (`~/.claude/projects/c--illustrated-narrator/*.jsonl`),
se queda con las que empezaron con la instrucción de lote (la que pega la lista
"YA ESTÁN HECHOS") y suma el `usage` de cada respuesta. Cuenta los guiones que
devolvió la sesión (los "slug" del bloque JSON final).

    .venv\\Scripts\\python.exe tools\\medir_tokens_lotes.py [desde AAAA-MM-DD]
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

CARPETA = Path.home() / ".claude" / "projects" / "c--illustrated-narrator"
desde = datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime(2026, 9, 28)


def texto_de(msg) -> str:
    c = msg.get("content")
    if isinstance(c, str):
        return c
    return " ".join(b.get("text", "") for b in c or [] if isinstance(b, dict))


filas = []
for f in sorted(CARPETA.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
    if datetime.fromtimestamp(f.stat().st_mtime) < desde:
        continue
    primero, tok, pasos, ultimo, inicio = None, {"in": 0, "cr": 0, "cc": 0, "out": 0}, 0, "", None
    vistos = set()  # una respuesta = varias líneas con el mismo usage (13/10/2026)
    for linea in f.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(linea)
        except ValueError:
            continue
        if inicio is None and d.get("timestamp"):
            inicio = d["timestamp"][:16]
        m = d.get("message") or {}
        if d.get("type") == "user" and primero is None:
            primero = texto_de(m)
        if d.get("type") == "assistant" and m.get("id") not in vistos:
            vistos.add(m.get("id"))
            u = m.get("usage") or {}
            tok["in"] += u.get("input_tokens", 0)
            tok["cr"] += u.get("cache_read_input_tokens", 0)
            tok["cc"] += u.get("cache_creation_input_tokens", 0)
            tok["out"] += u.get("output_tokens", 0)
            pasos += 1
            t = texto_de(m)
            if t.strip():
                ultimo = t
    if not primero or "YA ESTÁN HECHOS" not in primero:
        continue
    pedidos = re.search(r"(\d+)\s+guiones", primero)
    hechos = len(set(re.findall(r'"slug"\s*:\s*"([^"]+)"', ultimo)))
    total = sum(tok.values())
    filas.append((inicio, f.stem[:8], pedidos.group(1) if pedidos else "?", hechos, pasos, tok, total))

print(f"{'inicio':16} {'sesión':8} {'pedidos':>7} {'hechos':>6} {'pasos':>5} {'total (M)':>9} "
      f"{'lect.caché':>10} {'escr.caché':>10} {'salida':>8} {'M/guion':>8}")
for inicio, sid, ped, hechos, pasos, tok, total in filas:
    por = f"{total / hechos / 1e6:8.2f}" if hechos else "      --"
    print(f"{inicio:16} {sid:8} {ped:>7} {hechos:>6} {pasos:>5} {total / 1e6:9.1f} {tok['cr'] / 1e6:10.1f} "
          f"{tok['cc'] / 1e6:10.2f} {tok['out'] / 1e6:8.3f} {por}")
con = [f for f in filas if f[3]]
if con:
    t = sum(f[6] for f in con)
    g = sum(f[3] for f in con)
    print(f"\nTOTAL: {g} guiones en {len(con)} sesiones con resultado = {t / 1e6:.0f} M tokens "
          f"-> {t / g / 1e6:.2f} M por guion")
