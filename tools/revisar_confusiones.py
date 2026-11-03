"""Revisa si el inventario puede contestar "gancho o nota" antes de pedir metricas.

Un dato que solo existe en una ventana de tiempo no se puede comparar contra
otro de otra ventana: lo que cambie puede ser la portada o puede ser la fecha.
Esto mide ese traslape.

    python tools/revisar_confusiones.py
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "analisis" / "inventario_videos.csv"


def main() -> None:
    filas = list(csv.DictReader(CSV.open(encoding="utf-8-sig")))
    con_portada = [f for f in filas if f["portada"] != "sin portada"]
    gancho = [f for f in con_portada if f["portada"] == "gancho"]
    nota = [f for f in con_portada if f["portada"] == "nota"]

    print(f"con portada: {len(con_portada)}  (gancho {len(gancho)} / nota {len(nota)})\n")

    for nombre, grupo in (("gancho", gancho), ("nota", nota)):
        fechas = sorted(f["fecha"] for f in grupo)
        print(f"{nombre:7s} fechas: {fechas[0]} -> {fechas[-1]}  ({len(set(fechas))} dias distintos)")

    traslape = sorted({f["fecha"] for f in gancho} & {f["fecha"] for f in nota})
    print(f"\ndias con AMBAS portadas: {len(traslape)}  {traslape}")

    print("\n=== formula x portada ===")
    conteo = Counter((f["portada"], f["formula"]) for f in con_portada)
    formulas = sorted({f["formula"] for f in con_portada})
    print(f"{'formula':24s} {'gancho':>7s} {'nota':>6s}")
    for formula in formulas:
        print(f"{formula:24s} {conteo[('gancho', formula)]:7d} {conteo[('nota', formula)]:6d}")

    print("\n=== los 21 gancho, uno por uno ===")
    for f in sorted(gancho, key=lambda r: r["fecha"]):
        print(f"  {f['fecha']}  {f['formula']:22s} {f['estado_mx'] or '(sin estado)':18s} {f['lote']}")


if __name__ == "__main__":
    main()
