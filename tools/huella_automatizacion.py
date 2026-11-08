"""Mide que tan igual se ven los videos entre si.

La fórmula se cumple al 100% (ver cumplimiento_formula_2026-11-03.md). El riesgo
de eso es que el cumplimiento perfecto de una plantilla ES la huella de un
proceso automatizado: mismo esqueleto, misma apertura, mismo cierre, siempre.
Esto cuenta cuanto se repite literalmente.

    python tools/huella_automatizacion.py

Salida: analisis/huella_automatizacion.csv
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANDROID_IN = Path(r"C:\Android_in")
CSV_IN = RAIZ / "analisis" / "cumplimiento_formula.csv"
SALIDA = RAIZ / "analisis" / "huella_automatizacion.csv"

DEL_CANAL = {"contradiccion local", "viral", "polemica", "comparativa", "tradiciones"}
DESDE = "2026-10-14"  # desde que arranco la fabrica


def sin_acentos(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn")


def normal(t: str) -> str:
    return re.sub(r"\s+", " ", sin_acentos(t or "").lower()).strip()


def primeras(t: str, n: int) -> str:
    return " ".join(normal(t).split()[:n])


def main() -> None:
    base = [f for f in csv.DictReader(CSV_IN.open(encoding="utf-8-sig"))
            if f["formula"] in DEL_CANAL and f["fecha"] >= DESDE]

    filas = []
    for f in base:
        ruta = ANDROID_IN / f["slug"] / "guion.json"
        if not ruta.exists():
            continue
        try:
            guion = json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        planos = {str(p.get("id", "")): (p.get("narracion") or "") for p in guion.get("planos") or []}
        filas.append({
            "slug": f["slug"],
            "fecha": f["fecha"],
            "formula": f["formula"],
            "titulo": guion.get("titulo", ""),
            "p00": planos.get("p00", ""),
            "p01": planos.get("p01", ""),
            "p08": planos.get("p08", ""),
            "n_planos": len(guion.get("planos") or []),
            "ids": " ".join(planos),
            "hashtags": " ".join(guion.get("hashtags") or []),
        })

    n = len(filas)
    print(f"guiones del canal desde el {DESDE}: {n}\n")

    def pct(x: int) -> str:
        return f"{100 * x / n:3.0f}%"

    # 1. El esqueleto.
    print("=== 1. El esqueleto ===")
    esqueletos = Counter(f["ids"] for f in filas)
    for ids, c in esqueletos.most_common(3):
        print(f"  {pct(c)} ({c:3d})  {ids}")
    print(f"  esqueletos distintos: {len(esqueletos)}")

    # 2. El cierre p08.
    print("\n=== 2. El cierre (p08) ===")
    arranques = Counter(primeras(f["p08"], 6) for f in filas if f["p08"])
    for frase, c in arranques.most_common(3):
        print(f"  {pct(c)} ({c:3d})  \"{frase}...\"")
    cierres = Counter(normal(f["p08"].split("?")[-1]) for f in filas if f["p08"])
    print("  ultima frase despues de la pregunta:")
    for frase, c in cierres.most_common(3):
        print(f"    {pct(c)} ({c:3d})  \"{frase}\"")

    # 3. La apertura p01.
    print("\n=== 3. La apertura (p01) ===")
    ap = Counter(primeras(f["p01"], 3) for f in filas if f["p01"])
    for frase, c in ap.most_common(4):
        print(f"  {pct(c)} ({c:3d})  \"{frase}...\"")

    # 4. Forma del titulo: dos oraciones, la segunda cortita y seca.
    print("\n=== 4. Forma del titulo ===")
    dos_frases = 0
    remates: Counter[str] = Counter()
    for f in filas:
        partes = [p.strip() for p in re.split(r"(?<=[.!?])\s+", f["titulo"]) if p.strip()]
        if len(partes) >= 2 and len(partes[-1].split()) <= 6:
            dos_frases += 1
            remates[normal(partes[-1])] += 1
    print(f"  {pct(dos_frases)} ({dos_frases}) terminan en una segunda oracion de <=6 palabras")
    print("  remates que se repiten:")
    for frase, c in remates.most_common(6):
        if c > 1:
            print(f"    {c:3d}x  \"{frase}\"")

    # 5. Hashtags.
    print("\n=== 5. Hashtags ===")
    todos = Counter()
    for f in filas:
        for h in f["hashtags"].split():
            todos[h.lower()] += 1
    for h, c in todos.most_common(6):
        print(f"  {pct(c)} ({c:3d})  {h}")

    # 6. Arranque del p00, que es el primer segundo del video.
    print("\n=== 6. Primeras palabras del video (p00) ===")
    primera_palabra = Counter(normal(f["p00"]).split()[0] if f["p00"] else "" for f in filas)
    for w, c in primera_palabra.most_common(6):
        if w:
            print(f"  {pct(c)} ({c:3d})  \"{w}...\"")

    with SALIDA.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\ndetalle -> {SALIDA}")


if __name__ == "__main__":
    main()
