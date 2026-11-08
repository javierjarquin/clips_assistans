"""Mide la pregunta a la mitad con la ventana que dice la especificacion.

instruccion_cercania linea 124-128: una pregunta antes del segundo diez "en p01
o p02", y otra a la mitad "en p03, p04 o p05". El detector de
auditar_cumplimiento usa tercios por posicion, que no es lo mismo. Aqui se mide
por id de plano, para no reportar un numero peor que el real.

    python tools/pregunta_a_la_mitad.py
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANDROID_IN = Path(r"C:\Android_in")
CSV = RAIZ / "analisis" / "cumplimiento_formula.csv"

TEMPRANA = {"p01", "p02"}
MITAD = {"p03", "p04", "p05"}
DEL_CANAL = {"contradiccion local", "viral", "polemica", "comparativa", "tradiciones"}

SEGUNDA_PERSONA = re.compile(
    r"\b(tu|tus|ti|te|usted|ustedes|tuyo|tuya|contigo)\b", re.IGNORECASE
)


def sin_acentos(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn")


def main() -> None:
    filas = [f for f in csv.DictReader(CSV.open(encoding="utf-8-sig"))
             if f["formula"] in DEL_CANAL and f["fecha"] >= "2026-10-14"]

    resultados = []
    for f in filas:
        ruta = ANDROID_IN / f["slug"] / "guion.json"
        if not ruta.exists():
            continue
        try:
            planos = json.loads(ruta.read_text(encoding="utf-8")).get("planos") or []
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue

        por_zona = {"temprana": [], "mitad": [], "otra": []}
        for plano in planos:
            pid = str(plano.get("id", ""))
            voz = plano.get("narracion") or plano.get("voz") or ""
            for p in re.findall(r"¿([^?]*)\?", voz):
                if not SEGUNDA_PERSONA.search(sin_acentos(p)):
                    continue
                zona = "temprana" if pid in TEMPRANA else "mitad" if pid in MITAD else "otra"
                por_zona[zona].append((pid, p.strip()))

        resultados.append((f, por_zona))

    n = len(resultados)
    con_temprana = sum(1 for _, z in resultados if z["temprana"])
    con_mitad = sum(1 for _, z in resultados if z["mitad"])
    con_ambas = sum(1 for _, z in resultados if z["temprana"] and z["mitad"])

    print(f"guiones del canal desde el 14/10: {n}\n")
    print(f"  pregunta en p01/p02 (temprana): {con_temprana:3d}  {100*con_temprana/n:3.0f}%")
    print(f"  pregunta en p03/p04/p05 (mitad): {con_mitad:3d}  {100*con_mitad/n:3.0f}%")
    print(f"  LAS DOS, como pide la formula:   {con_ambas:3d}  {100*con_ambas/n:3.0f}%")

    # Donde si caen las preguntas, para ver el hueco.
    print("\n=== donde caen las preguntas a quien ve (todas) ===")
    conteo: dict[str, int] = {}
    for _, z in resultados:
        for zona in z:
            for pid, _p in z[zona]:
                conteo[pid] = conteo.get(pid, 0) + 1
    for pid in sorted(conteo):
        marca = ""
        if pid in TEMPRANA:
            marca = "  <- ventana temprana"
        elif pid in MITAD:
            marca = "  <- ventana de la mitad"
        print(f"  {pid}: {conteo[pid]:3d}{marca}")

    print("\n=== ejemplos de guiones SIN pregunta en la ventana de la mitad ===")
    faltan = [(f, z) for f, z in resultados if not z["mitad"]]
    print(f"  {len(faltan)} de {n}\n")
    for f, z in faltan[:5]:
        print(f"  {f['fecha']} {f['slug']}")
        for zona in ("temprana", "otra"):
            for pid, p in z[zona][:3]:
                print(f"      {pid} ({zona}): ¿{p}?")


if __name__ == "__main__":
    main()
