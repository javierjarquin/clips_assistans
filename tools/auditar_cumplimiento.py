"""Mide si los guiones cumplen la formula que escribimos.

No necesita metricas de TikTok: compara lo producido contra la especificacion
en instruccion_cercania.py. Revisa cuatro cosas:

  1. mezcla de vigencias contra MEZCLA = 3 conversacion : 2 perenne
  2. preguntas a quien ve: desde el 21/10/2026 TODAS deben ser de si o no
  3. que haya pregunta temprana y pregunta a la mitad, mas el cierre p08
  4. que el plus este completo (contradiccion, portada 3-5 palabras, mapa)

    python tools/auditar_cumplimiento.py

Salida: analisis/cumplimiento_formula.csv
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANDROID_IN = Path(r"C:\Android_in")
INVENTARIO = RAIZ / "analisis" / "inventario_videos.csv"
SALIDA = RAIZ / "analisis" / "cumplimiento_formula.csv"

# La regla "toda pregunta a quien ve es de si o no" entro el 21/10/2026.
REGLA_SINO_DESDE = "2026-10-21"

MEZCLA_OBJETIVO = {"conversacion": 3, "perenne": 2}

# Marcas de segunda persona: si la pregunta las trae, va dirigida a quien ve.
SEGUNDA_PERSONA = re.compile(
    r"\b(tu|tus|ti|te|usted|ustedes|tuyo|tuya|contigo)\b", re.IGNORECASE
)

# Si empieza con una de estas, no es de si o no.
ABIERTAS = re.compile(
    r"^\s*(que|como|por que|porque|cual|cuales|cuando|quien|quienes|donde|"
    r"cuanto|cuanta|cuantos|cuantas|a que|de que|con que|para que)\b"
)


def sin_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto or "")
        if unicodedata.category(c) != "Mn"
    )


def preguntas(texto: str) -> list[str]:
    """Saca las preguntas de un bloque de narracion."""
    return [p.strip() for p in re.findall(r"¿([^?]*)\?", texto or "") if p.strip()]


def es_de_si_o_no(pregunta: str) -> bool:
    plano = sin_acentos(pregunta).lower().strip()
    if ABIERTAS.match(plano):
        return False
    # "¿A o B?" y las que arrancan con "o": la voz las lee como opcion.
    if plano.startswith("o "):
        return False
    return True


def main() -> None:
    inventario = list(csv.DictReader(INVENTARIO.open(encoding="utf-8-sig")))
    fecha_de = {f["slug_guion"]: f["fecha"] for f in inventario if f["slug_guion"]}
    formula_de = {f["slug_guion"]: f["formula"] for f in inventario if f["slug_guion"]}
    vigencia_de = {f["slug_guion"]: f["vigencia"] for f in inventario if f["slug_guion"]}

    filas = []
    for slug, fecha in sorted(fecha_de.items(), key=lambda kv: kv[1]):
        ruta = ANDROID_IN / slug / "guion.json"
        if not ruta.exists():
            continue
        try:
            guion = json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue

        planos = guion.get("planos") or []
        if not planos:
            continue
        total = len(planos)
        plus = guion.get("plus") or {}

        a_quien_ve: list[tuple[int, str]] = []
        for i, plano in enumerate(planos):
            voz = plano.get("narracion") or plano.get("voz") or ""
            for p in preguntas(voz):
                if SEGUNDA_PERSONA.search(sin_acentos(p)):
                    a_quien_ve.append((i, p))

        malas = [p for _, p in a_quien_ve if not es_de_si_o_no(p)]
        # Temprana = primer tercio; media = tercio de en medio.
        temprana = any(i <= max(1, total // 3) for i, _ in a_quien_ve)
        media = any(total // 3 < i <= 2 * total // 3 for i, _ in a_quien_ve)

        ids = [str(p.get("id", "")) for p in planos]
        cierre = next((p for p in planos if str(p.get("id")) == "p08"), None)
        voz_cierre = (cierre or {}).get("narracion", "") if cierre else ""
        cierre_ok = bool(cierre) and bool(preguntas(voz_cierre))

        portada = plus.get("portada") or {}
        texto_portada = portada.get("texto", "") if isinstance(portada, dict) else ""
        n_palabras = len(texto_portada.split()) if texto_portada else 0

        filas.append({
            "slug": slug,
            "fecha": fecha,
            "formula": formula_de.get(slug, ""),
            "vigencia": vigencia_de.get(slug, ""),
            "n_planos": total,
            "tiene_p08": "si" if cierre else "no",
            "preguntas_a_quien_ve": len(a_quien_ve),
            "preguntas_no_sino": len(malas),
            "ejemplo_mala": malas[0][:70] if malas else "",
            "pregunta_temprana": "si" if temprana else "no",
            "pregunta_media": "si" if media else "no",
            "cierre_con_pregunta": "si" if cierre_ok else "no",
            "tiene_contradiccion": "si" if plus.get("contradiccion") else "no",
            "tiene_mapa": "si" if plus.get("mapa") else "no",
            "palabras_portada": n_palabras,
            "portada_3a5": "si" if 3 <= n_palabras <= 5 else "no",
            "n_evidencia": len(guion.get("evidencia") or []),
            "ids_planos": " ".join(ids),
        })

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} guiones revisados -> {SALIDA}\n")

    def pct(n: int, de: int) -> str:
        return f"{100 * n / de:.0f}%" if de else "-"

    # 1. Mezcla de vigencias.
    print("=== 1. Mezcla de vigencias (objetivo 3 conversacion : 2 perenne) ===")
    con = sum(1 for f in filas if f["vigencia"] == "conversacion")
    per = sum(1 for f in filas if f["vigencia"] == "perenne")
    if con + per:
        objetivo = MEZCLA_OBJETIVO["conversacion"] / sum(MEZCLA_OBJETIVO.values())
        print(f"  conversacion {con}  perenne {per}   real {pct(con, con + per)} "
              f"conversacion vs objetivo {objetivo * 100:.0f}%")
        if con / (con + per) > objetivo + 0.08:
            print("  >> DESVIADO hacia lo efimero: menos piezas que envejecen bien")

    # 2. Regla de si o no, antes y despues del 21/10.
    print("\n=== 2. Preguntas a quien ve: regla de si o no (desde 21/10/2026) ===")
    for etiqueta, grupo in (
        ("antes del 21/10", [f for f in filas if f["fecha"] < REGLA_SINO_DESDE]),
        ("desde el 21/10", [f for f in filas if f["fecha"] >= REGLA_SINO_DESDE]),
    ):
        con_pregunta = [f for f in grupo if f["preguntas_a_quien_ve"]]
        rompen = [f for f in grupo if f["preguntas_no_sino"]]
        print(f"  {etiqueta:16s} guiones {len(grupo):4d}  con pregunta a quien ve "
              f"{len(con_pregunta):4d}  rompen la regla {len(rompen):4d} "
              f"({pct(len(rompen), len(con_pregunta))} de los que preguntan)")
        for f in rompen[:4]:
            print(f"        {f['fecha']} {f['slug'][:42]:42s} \"{f['ejemplo_mala']}\"")

    # 3. Las dos preguntas y el cierre.
    print("\n=== 3. Colocacion de las preguntas ===")
    n = len(filas)
    print(f"  pregunta temprana (primer tercio): {pct(sum(1 for f in filas if f['pregunta_temprana'] == 'si'), n)}")
    print(f"  pregunta a la mitad:               {pct(sum(1 for f in filas if f['pregunta_media'] == 'si'), n)}")
    print(f"  las dos:                           {pct(sum(1 for f in filas if f['pregunta_temprana'] == 'si' and f['pregunta_media'] == 'si'), n)}")
    print(f"  cierre p08 con pregunta:           {pct(sum(1 for f in filas if f['cierre_con_pregunta'] == 'si'), n)}")
    print(f"  cero preguntas a quien ve:         {pct(sum(1 for f in filas if not f['preguntas_a_quien_ve']), n)}")

    # 4. El plus.
    print("\n=== 4. Plus completo ===")
    print(f"  con contradiccion: {pct(sum(1 for f in filas if f['tiene_contradiccion'] == 'si'), n)}")
    print(f"  con mapa:          {pct(sum(1 for f in filas if f['tiene_mapa'] == 'si'), n)}")
    print(f"  portada 3-5 pal.:  {pct(sum(1 for f in filas if f['portada_3a5'] == 'si'), n)}")
    sin_ev = sum(1 for f in filas if f["n_evidencia"] == 0)
    print(f"  SIN evidencia:     {pct(sin_ev, n)}  ({sin_ev} guiones)")


if __name__ == "__main__":
    main()
