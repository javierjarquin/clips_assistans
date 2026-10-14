"""¿Cuántos tokens caben en la cuota de Claude antes del límite? (12/10/2026)

Busca en TODAS las sesiones de la cuenta (bot e IDE comparten cuota) los
avisos "hit your ... limit" y suma lo gastado en las 5 horas anteriores a
cada uno, por tipo de token.

    .venv\\Scripts\\python.exe tools\\medir_cuota_claude.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path.home() / ".claude" / "projects"
VENTANA = timedelta(hours=5)

uso = []      # (momento, input, cache_read, cache_creation, output, carpeta)
limites = []  # (momento, texto)
# Una respuesta ocupa varias líneas con el mismo id y el mismo usage: se cuenta
# una vez (13/10/2026; antes salía ~3 veces de más).
vistos = set()
for f in RAIZ.glob("*/*.jsonl"):
    for linea in f.open(encoding="utf-8", errors="replace"):
        if '"usage"' not in linea and "limit" not in linea:
            continue
        try:
            d = json.loads(linea)
        except ValueError:
            continue
        ts = d.get("timestamp")
        if not ts:
            continue
        t = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        m = d.get("message") or {}
        u = m.get("usage") if isinstance(m, dict) else None
        if d.get("type") == "assistant" and u and m.get("id") not in vistos:
            vistos.add(m.get("id"))
            uso.append((t, u.get("input_tokens", 0), u.get("cache_read_input_tokens", 0),
                        u.get("cache_creation_input_tokens", 0), u.get("output_tokens", 0), f.parent.name))
        texto = json.dumps(m, ensure_ascii=False) if isinstance(m, dict) else ""
        if "hit your" in texto.lower() and "limit" in texto.lower():
            limites.append((t, texto[:160]))

uso.sort()
vistos = []
for t, txt in sorted(limites):
    if vistos and t - vistos[-1] < timedelta(minutes=30):
        continue  # varios avisos del mismo corte
    vistos.append(t)
    ventana = [u for u in uso if t - VENTANA <= u[0] <= t]
    tot = [sum(u[i] for u in ventana) for i in range(1, 5)]
    print(f"{t:%Y-%m-%d %H:%M} UTC | 5 h antes: total {sum(tot) / 1e6:6.1f} M "
          f"(lect.caché {tot[1] / 1e6:6.1f}, escr.caché {tot[2] / 1e6:5.2f}, entrada {tot[0] / 1e6:5.2f}, "
          f"salida {tot[3] / 1e6:5.2f}) en {len(ventana)} pasos")
if not vistos:
    print("No encontré avisos de límite en los historiales.")

# Gasto por día, para dimensionar
por_dia: dict[str, list[float]] = {}
for t, i, cr, cc, o, carpeta in uso:
    por_dia.setdefault(f"{t:%Y-%m-%d}", [0, 0, 0, 0])
    for k, v in enumerate((i, cr, cc, o)):
        por_dia[f"{t:%Y-%m-%d}"][k] += v
print("\nGasto por día (últimos 14):")
for dia in sorted(por_dia)[-14:]:
    i, cr, cc, o = por_dia[dia]
    print(f"{dia}: total {(i + cr + cc + o) / 1e6:6.0f} M | escr.caché {cc / 1e6:5.1f} M | salida {o / 1e6:4.2f} M")
