"""Separa el cumplimiento por epoca, para no confundir "se dejo de cumplir"
con "la regla todavia no existia".

    python tools/cumplimiento_por_epoca.py
"""

from __future__ import annotations

import csv
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "analisis" / "cumplimiento_formula.csv"

EPOCAS = [
    ("antes de la fabrica", "0000-00-00", "2026-10-13"),
    ("fabrica temprana", "2026-10-14", "2026-10-20"),
    ("desde la regla si/no", "2026-10-21", "9999-99-99"),
]

# Solo las formulas del canal: trivia y POCs no se rigen por esto.
DEL_CANAL = {"contradiccion local", "viral", "polemica", "comparativa", "tradiciones"}


def main() -> None:
    filas = [f for f in csv.DictReader(CSV.open(encoding="utf-8-sig"))
             if f["formula"] in DEL_CANAL]
    print(f"guiones de formulas del canal: {len(filas)}\n")

    def pct(n: int, de: int) -> str:
        return f"{100 * n / de:3.0f}%" if de else "  -"

    cols = ["n", "temprana", "mitad", "las dos", "p08 preg", "contradicc", "mapa", "sin evid"]
    print(f"{'epoca':22s} " + " ".join(f"{c:>10s}" for c in cols))

    for nombre, desde, hasta in EPOCAS:
        g = [f for f in filas if desde <= f["fecha"] <= hasta]
        if not g:
            continue
        n = len(g)
        vals = [
            str(n),
            pct(sum(1 for f in g if f["pregunta_temprana"] == "si"), n),
            pct(sum(1 for f in g if f["pregunta_media"] == "si"), n),
            pct(sum(1 for f in g if f["pregunta_temprana"] == "si"
                    and f["pregunta_media"] == "si"), n),
            pct(sum(1 for f in g if f["cierre_con_pregunta"] == "si"), n),
            pct(sum(1 for f in g if f["tiene_contradiccion"] == "si"), n),
            pct(sum(1 for f in g if f["tiene_mapa"] == "si"), n),
            pct(sum(1 for f in g if f["n_evidencia"] == "0"), n),
        ]
        print(f"{nombre:22s} " + " ".join(f"{v:>10s}" for v in vals))

    # Mezcla de vigencias por epoca.
    print("\n=== mezcla de vigencias por epoca (objetivo 60% conversacion) ===")
    for nombre, desde, hasta in EPOCAS:
        g = [f for f in filas if desde <= f["fecha"] <= hasta]
        con = sum(1 for f in g if f["vigencia"] == "conversacion")
        per = sum(1 for f in g if f["vigencia"] == "perenne")
        if con + per:
            print(f"  {nombre:22s} conversacion {con:3d}  perenne {per:3d}  -> "
                  f"{100 * con / (con + per):3.0f}% conversacion")

    # La pregunta a la mitad, que es la que mas se cae.
    print("\n=== guiones recientes SIN pregunta a la mitad ===")
    recientes = [f for f in filas if f["fecha"] >= "2026-10-21"]
    faltan = [f for f in recientes if f["pregunta_media"] == "no"]
    print(f"  {len(faltan)} de {len(recientes)} guiones desde el 21/10")
    for f in faltan[:12]:
        print(f"    {f['fecha']} {f['formula']:20s} {f['slug'][:46]:46s} "
              f"preguntas={f['preguntas_a_quien_ve']}")


if __name__ == "__main__":
    main()
