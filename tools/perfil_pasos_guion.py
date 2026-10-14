"""Perfil de las sesiones del bot que escriben guiones (13/10/2026).

Para cada sesión reciente de `~/.claude/projects/c--illustrated-narrator/`:
cuántos pasos (respuestas de Claude) dio, cuánto contexto relee en promedio
cada paso, qué herramientas usó y con qué modelo. Sirve para saber si el gasto
viene de leer páginas o de dar muchos pasos con un contexto grande.

    .venv\\Scripts\\python.exe tools\\perfil_pasos_guion.py [desde AAAA-MM-DD]
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

CARPETA = Path.home() / ".claude" / "projects" / "c--illustrated-narrator"
desde = datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime(2026, 10, 12)

for f in sorted(CARPETA.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
    if datetime.fromtimestamp(f.stat().st_mtime) < desde:
        continue
    pasos, contexto, salida, primero = 0, [], 0, None
    herramientas, modelos = Counter(), Counter()
    vistos = set()
    for linea in f.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(linea)
        except ValueError:
            continue
        m = d.get("message") or {}
        if d.get("type") == "user" and primero is None:
            c = m.get("content")
            primero = c if isinstance(c, str) else " ".join(
                b.get("text", "") for b in c or [] if isinstance(b, dict))
        if d.get("type") != "assistant":
            continue
        for b in m.get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                herramientas[b.get("name")] += 1
        # Una respuesta llega partida en varias líneas con el mismo id y el
        # mismo usage: se cuenta una sola vez.
        if m.get("id") in vistos:
            continue
        vistos.add(m.get("id"))
        u = m.get("usage") or {}
        pasos += 1
        modelos[m.get("model", "?")] += 1
        contexto.append(u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                        + u.get("cache_creation_input_tokens", 0))
        salida += u.get("output_tokens", 0)
    if not pasos:
        continue
    total = sum(contexto) + salida
    print(f"\n{f.stem[:8]}  {datetime.fromtimestamp(f.stat().st_mtime):%d/%m %H:%M}  "
          f"{(primero or '')[:70]!r}")
    print(f"  pasos {pasos}  total {total / 1e6:.1f} M  contexto/paso: inicio {contexto[0] / 1e3:.0f}k, "
          f"prom {sum(contexto) / pasos / 1e3:.0f}k, final {contexto[-1] / 1e3:.0f}k  salida {salida / 1e3:.0f}k")
    print(f"  modelos {dict(modelos)}")
    print(f"  herramientas {dict(herramientas.most_common(8))}")
