"""Flujo viejo contra flujo ligero, escribiendo un guion de cero cada uno (13/10/2026).

Usa la misma función que la fábrica (`fabrica._guiones_de_cercania`), una vez
con la sesión de antes y otra con la ligera, uno después del otro (si corren a
la vez pueden agarrar la misma noticia y pisarse el guion.json). Mide pasos,
tokens (sin duplicados), minutos y lo que dice la revisión automática.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\comparar_flujos.py cancun
"""

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\dato-mata-gato-bot\src")
from dato_mata_gato_bot import claude_runner, fabrica, herramientas_guion  # noqa: E402

SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "comparacion_flujos.json"


def pasos(sid: str) -> int:
    for c in (claude_runner.carpeta_de_sesiones(claude_runner.CWD),
              claude_runner.carpeta_de_sesiones(claude_runner.CWD_LIGERO)):
        ruta = c / f"{sid}.jsonl"
        if ruta.exists():
            ids = set()
            for linea in ruta.open(encoding="utf-8", errors="replace"):
                d = json.loads(linea)
                if d.get("type") == "assistant":
                    ids.add((d.get("message") or {}).get("id"))
            return len(ids)
    return 0


def correr(clave: str, ligera: bool) -> dict:
    inicio = time.time()
    guiones, sesiones = asyncio.run(fabrica._guiones_de_cercania(fabrica._Avisador(), clave, 1, ligera=ligera))
    tok = fabrica.tokens_de_sesiones(sesiones)
    slugs = [g["slug"] for g in guiones if g.get("slug")]
    return {"flujo": "ligero" if ligera else "viejo", "slugs": slugs, "sesiones": sesiones,
            "pasos": sum(pasos(s) for s in sesiones), "tokens": tok,
            "minutos": round((time.time() - inicio) / 60, 1),
            "revision": {s: herramientas_guion.revisar(s) for s in slugs}}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from dotenv import load_dotenv
    load_dotenv(r"C:\dato-mata-gato-bot\.env")
    clave = sys.argv[1] if len(sys.argv) > 1 else "cancun"
    resultados = []
    for ligera in (False, True):
        r = correr(clave, ligera)
        resultados.append(r)
        SALIDA.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{r['flujo']}: {r['slugs']} · {r['pasos']} pasos · {r['tokens']['total'] / 1e6:.2f} M tokens "
              f"· {r['minutos']} min", flush=True)
    print(f"RESULTADO {SALIDA}")
