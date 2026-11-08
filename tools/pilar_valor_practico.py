"""Mide cuantos guiones traen el pilar 7 (valor practico), que es el palanca
de los COMPARTIDOS y es el unico que la instruccion marca como opcional.

Berger: lo util se comparte para ayudar a otros. Los pilares 1 al 6 son
obligatorios y empujan retencion y comentarios; el 7 empuja compartidos y no
es obligatorio. Esto cuenta la diferencia.

    python tools/pilar_valor_practico.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANDROID_IN = Path(r"C:\Android_in")
CSV_IN = RAIZ / "analisis" / "cumplimiento_formula.csv"

DEL_CANAL = {"contradiccion local", "viral", "polemica", "comparativa", "tradiciones"}
DESDE = "2026-10-14"


def main() -> None:
    base = [f for f in csv.DictReader(CSV_IN.open(encoding="utf-8-sig"))
            if f["formula"] in DEL_CANAL and f["fecha"] >= DESDE]

    total = 0
    con_condiciones = 0
    llaves = Counter()
    con_7 = []
    sin_7 = []

    for f in base:
        ruta = ANDROID_IN / f["slug"] / "guion.json"
        if not ruta.exists():
            continue
        try:
            guion = json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        total += 1
        cond = ((guion.get("_schema") or {}).get("condiciones")) or {}
        if cond:
            con_condiciones += 1
            for k in cond:
                llaves[k] += 1
        valor = ""
        for k, v in cond.items():
            if "valor_practico" in k or k.startswith("7"):
                valor = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        if valor and valor.strip() and valor.strip().lower() not in {"no", "ninguno", "n/a", "-"}:
            con_7.append((f, valor))
        else:
            sin_7.append(f)

    print(f"guiones revisados: {total}")
    print(f"con _schema.condiciones: {con_condiciones}\n")

    print("=== llaves de condiciones que aparecen ===")
    for k, c in sorted(llaves.items()):
        marca = "  <- el de compartidos" if ("valor" in k or k.startswith("7")) else ""
        print(f"  {c:4d} ({100*c/max(1,total):3.0f}%)  {k}{marca}")

    print(f"\n=== pilar 7 (valor practico) ===")
    print(f"  CON valor practico: {len(con_7):3d}  ({100*len(con_7)/max(1,total):3.0f}%)")
    print(f"  SIN valor practico: {len(sin_7):3d}  ({100*len(sin_7)/max(1,total):3.0f}%)")

    if con_7:
        print("\n  ejemplos de los que si lo traen:")
        for f, v in con_7[:5]:
            print(f"    {f['slug'][:44]:44s} {v[:84]}")


if __name__ == "__main__":
    main()
