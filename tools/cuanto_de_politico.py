"""Mide que tan politico es el corpus, y de donde le sale lo politico.

Hipotesis de Javier (03/11/2026): los videos se sienten muy politicos y eso
puede estar costando alcance. La pieza 4 de la formula (coraje) pide "alguien
con nombre o institucion responsable que no cumplio, cobro de mas, prometio y
no hizo" -- y el responsable de una contradiccion local casi siempre es un
organo de gobierno. Esto mide si lo politico es deriva o es la formula.

    python tools/cuanto_de_politico.py

Salida: analisis/cuanto_de_politico.csv
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
SALIDA = RAIZ / "analisis" / "cuanto_de_politico.csv"

DEL_CANAL = {"contradiccion local", "viral", "polemica", "comparativa", "tradiciones"}
DESDE = "2026-10-14"

# Actores de gobierno o partido: lo que TikTok lee como politico.
GOBIERNO = [
    "ayuntamiento", "alcaldia", "alcalde", "alcaldesa", "presidenta municipal",
    "presidente municipal", "cabildo", "regidor", "regidores", "sindico",
    "gobernador", "gobernadora", "gobierno del estado", "gobierno federal",
    "secretaria de", "secretario de", "sedena", "semarnat", "profepa", "conagua",
    "sct", "sep", "imss", "issste", "cfe", "pemex", "fiscalia", "fge", "fgr",
    "congreso", "diputado", "diputada", "diputados", "senado", "senador",
    "presidenta", "presidente de la republica", "sheinbaum", "morena", "pri",
    "pan", "prd", "pvem", "movimiento ciudadano", "ine", "inegi", "paot",
    "profeco", "asamblea", "legislatura", "municipio", "estado de",
    "administracion municipal", "funcionario", "funcionarios", "autoridad",
    "autoridades", "licitacion", "obra publica", "presupuesto", "erario",
    "transparencia", "auditoria superior", "contraloria",
]

# Actores privados o no politicos.
PRIVADO = [
    "empresa", "concesionaria", "aguakan", "constructora", "hotel", "restaurante",
    "tienda", "cadena", "banco", "aseguradora", "inmobiliaria", "desarrollador",
    "patron", "patrones", "franquicia", "proveedor", "transportista",
    "influencer", "creadora", "creador", "podcast", "youtuber", "tiktoker",
    "marca", "comercio", "negocio", "particular", "vecino", "vecinos",
]

PARTIDISTA = ["morena", "pri", "pan", "prd", "pvem", "movimiento ciudadano",
              "oposicion", "partido", "eleccion", "elecciones", "campana",
              "candidato", "candidata", "voto", "votamos", "sufragio"]


def plano(t: str) -> str:
    sin = "".join(c for c in unicodedata.normalize("NFD", t or "")
                  if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", sin.lower())


def cuenta(texto: str, terminos: list[str]) -> list[str]:
    p = plano(texto)
    return sorted({t for t in terminos if re.search(rf"\b{re.escape(t)}\b", p)})


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

        narracion = " ".join((p.get("narracion") or "") for p in guion.get("planos") or [])
        cond = ((guion.get("_schema") or {}).get("condiciones")) or {}
        coraje = ""
        for k, v in cond.items():
            if k.startswith("4") or "coraje" in k:
                coraje = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        todo = f"{guion.get('titulo','')} {narracion} {coraje}"

        gob = cuenta(todo, GOBIERNO)
        priv = cuenta(todo, PRIVADO)
        part = cuenta(todo, PARTIDISTA)
        # El responsable de la pieza 4 es lo que de verdad define el tono.
        gob_coraje = cuenta(coraje, GOBIERNO)

        if gob and not priv:
            clase = "solo gobierno"
        elif gob and priv:
            clase = "mixto"
        elif priv and not gob:
            clase = "solo privado"
        else:
            clase = "sin actor"

        filas.append({
            "slug": f["slug"],
            "fecha": f["fecha"],
            "formula": f["formula"],
            "clase": clase,
            "responsable_es_gobierno": "si" if gob_coraje else "no",
            "n_terminos_gobierno": len(gob),
            "n_terminos_privado": len(priv),
            "partidista": "si" if part else "no",
            "terminos_partidistas": ", ".join(part),
            "gobierno": ", ".join(gob[:8]),
            "privado": ", ".join(priv[:6]),
            "titulo": guion.get("titulo", ""),
        })

    n = len(filas)
    print(f"guiones del canal desde el {DESDE}: {n}\n")

    def pct(x: int) -> str:
        return f"{100 * x / n:3.0f}%"

    print("=== 1. Quien es el actor del video ===")
    for clase, c in Counter(f["clase"] for f in filas).most_common():
        print(f"  {pct(c)} ({c:3d})  {clase}")

    print("\n=== 2. El responsable de la pieza 4 (coraje) ===")
    gob_c = sum(1 for f in filas if f["responsable_es_gobierno"] == "si")
    print(f"  es gobierno:    {pct(gob_c)} ({gob_c})")
    print(f"  no es gobierno: {pct(n - gob_c)} ({n - gob_c})")

    print("\n=== 3. Lenguaje partidista o electoral (el que mas pesa) ===")
    part = [f for f in filas if f["partidista"] == "si"]
    print(f"  {pct(len(part))} ({len(part)}) mencionan partido, eleccion, voto o candidato")
    terminos = Counter()
    for f in part:
        for t in f["terminos_partidistas"].split(", "):
            if t:
                terminos[t] += 1
    for t, c in terminos.most_common(8):
        print(f"      {c:3d}x  {t}")

    print("\n=== 4. Por formula ===")
    print(f"  {'formula':22s} {'n':>4s} {'solo gob':>9s} {'resp.=gob':>10s} {'partidista':>11s}")
    for formula in sorted({f["formula"] for f in filas}):
        g = [f for f in filas if f["formula"] == formula]
        sg = sum(1 for f in g if f["clase"] == "solo gobierno")
        rg = sum(1 for f in g if f["responsable_es_gobierno"] == "si")
        pa = sum(1 for f in g if f["partidista"] == "si")
        print(f"  {formula:22s} {len(g):4d} {100*sg/len(g):8.0f}% "
              f"{100*rg/len(g):9.0f}% {100*pa/len(g):10.0f}%")

    print("\n=== 5. Instituciones mas nombradas ===")
    inst = Counter()
    for f in filas:
        for t in f["gobierno"].split(", "):
            if t:
                inst[t] += 1
    for t, c in inst.most_common(12):
        print(f"  {c:3d}  {t}")

    with SALIDA.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\ndetalle -> {SALIDA}")


if __name__ == "__main__":
    main()
