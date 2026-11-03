"""Inventario de todo lo producido, listo para cruzar con el export de TikTok.

Arma una fila por video en C:\\Android_in\\lotes, con su lote, formula, estado,
portada y fecha. Las columnas de metricas quedan vacias: se llenan empalmando
el export de TikTok Studio (Analytics > Descargar datos) con empalmar_tiktok.py.

    python tools/auditar_formula.py

Salida: analisis/inventario_videos.csv
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

ANDROID_IN = Path(r"C:\Android_in")
LOTES = ANDROID_IN / "lotes"
FABRICA = ANDROID_IN / "fabrica"
SALIDA = Path(__file__).resolve().parent.parent / "analisis" / "inventario_videos.csv"

ESTADOS_MX = [
    "Aguascalientes", "Baja California Sur", "Baja California", "Campeche",
    "Chiapas", "Chihuahua", "Coahuila", "Colima", "Ciudad de Mexico",
    "Durango", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco",
    "Estado de Mexico", "Michoacan", "Morelos", "Nayarit", "Nuevo Leon",
    "Oaxaca", "Puebla", "Queretaro", "Quintana Roo", "San Luis Potosi",
    "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz",
    "Yucatan", "Zacatecas",
]

# Ciudades que aparecen seguido y cuyo estado no se puede adivinar del nombre.
CIUDAD_A_ESTADO = {
    "cancun": "Quintana Roo", "playa del carmen": "Quintana Roo",
    "chetumal": "Quintana Roo", "tulum": "Quintana Roo",
    "iztapalapa": "Ciudad de Mexico", "benito juarez": "Ciudad de Mexico",
    "gustavo a madero": "Ciudad de Mexico", "coyoacan": "Ciudad de Mexico",
    "xochimilco": "Ciudad de Mexico", "tlalpan": "Ciudad de Mexico",
    "cdmx": "Ciudad de Mexico",
    "ecatepec": "Estado de Mexico", "tlalnepantla": "Estado de Mexico",
    "naucalpan": "Estado de Mexico", "toluca": "Estado de Mexico",
    "nezahualcoyotl": "Estado de Mexico",
    "xilitla": "San Luis Potosi", "merida": "Yucatan",
    "guadalajara": "Jalisco", "zapopan": "Jalisco",
    "monterrey": "Nuevo Leon", "mulege": "Baja California Sur",
    "vizcaino": "Baja California Sur", "tijuana": "Baja California",
    "acapulco": "Guerrero", "puerto vallarta": "Jalisco",
    "veracruz": "Veracruz", "oaxaca": "Oaxaca", "puebla": "Puebla",
}

# Prefijo del slug -> formula. El formato del lote es el desempate.
PREFIJO_A_FORMULA = {
    "guion-viral": "viral",
    "guion-polemica": "polemica",
    "guion-comparativa": "comparativa",
    "guion-tradicion": "tradiciones",
    "guion-cancun": "contradiccion local",
    "guion-cdmx": "contradiccion local",
    "guion-tt": "tendencia tiktok",
}

FORMATO_A_FORMULA = {
    "redes": "contradiccion local",
    "viral": "viral",
    "tradiciones": "tradiciones",
    "cercania": "contradiccion local",
}

# La portada "gancho" fue la de defecto en esta ventana (ver analisis/guia_portadas.md).
GANCHO_DESDE = datetime(2026, 10, 29)
GANCHO_HASTA = datetime(2026, 11, 3, 23, 59, 59)


def plano(texto: str) -> str:
    """Quita acentos y todo lo que no sea alfanumerico, como hace el render."""
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]", "", sin_acentos.lower())


def leer_json(ruta: Path) -> dict | None:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def indexar_guiones() -> dict[str, dict]:
    """normalize(titulo) -> datos del guion, para amarrar el mp4 a su guion."""
    por_titulo: dict[str, dict] = {}
    for carpeta in ANDROID_IN.iterdir():
        if not carpeta.is_dir():
            continue
        guion = leer_json(carpeta / "guion.json")
        if not guion or not guion.get("titulo"):
            continue
        plus = guion.get("plus") or {}
        mapa = plus.get("mapa") or {}
        portada = plus.get("portada") or {}
        por_titulo[plano(guion["titulo"])] = {
            "slug": carpeta.name,
            "titulo": guion["titulo"],
            "etiqueta_mapa": mapa.get("etiqueta", ""),
            "consulta_mapa": mapa.get("consulta", ""),
            "texto_portada": portada.get("texto", "") if isinstance(portada, dict) else "",
            "hashtags": " ".join(guion.get("hashtags") or []),
            "n_planos": len(guion.get("planos") or []),
            "n_evidencia": len(guion.get("evidencia") or []),
        }
    return por_titulo


def indexar_fabrica() -> dict[str, dict]:
    """slug del guion -> lote y formato que lo produjo."""
    por_slug: dict[str, dict] = {}
    for carpeta in sorted(FABRICA.iterdir()):
        estado = leer_json(carpeta / "estado.json") if carpeta.is_dir() else None
        if not estado:
            continue
        creado = (estado.get("creado") or "")[:10]
        for slug, info in (estado.get("videos") or {}).items():
            por_slug[slug] = {
                "lote_fabrica": estado.get("lote", carpeta.name),
                "formato_lote": estado.get("formato", ""),
                "creado_lote": creado,
                "estado_produccion": (info or {}).get("estado", ""),
                "vigencia": (info or {}).get("vigencia", ""),
                "intentos": (info or {}).get("intentos", ""),
            }
    return por_slug


def deducir_estado(*fuentes: str) -> str:
    """Busca un estado de Mexico en la etiqueta del mapa, hashtags o el slug."""
    texto = plano(" ".join(f for f in fuentes if f))
    for estado in ESTADOS_MX:
        if plano(estado) in texto:
            return estado
    for ciudad, estado in CIUDAD_A_ESTADO.items():
        if plano(ciudad) in texto:
            return estado
    return ""


def tipo_portada(carpeta: Path, base: str) -> str:
    for sufijo, tipo in (
        ("_portada_gancho.jpg", "gancho"),
        ("_portada_nota.jpg", "nota"),
        ("_portada.jpg", "nota"),
    ):
        if (carpeta / f"{base}{sufijo}").exists():
            return tipo
    return "sin portada"


def main() -> None:
    guiones = indexar_guiones()
    fabrica = indexar_fabrica()
    filas = []

    for lote in sorted(LOTES.iterdir()):
        if not lote.is_dir():
            continue
        for mp4 in sorted(lote.glob("*.mp4")):
            base = mp4.stem
            guion = guiones.get(plano(base), {})
            slug = guion.get("slug", "")
            prod = fabrica.get(slug, {})

            formula = PREFIJO_A_FORMULA.get(
                "-".join(slug.split("-")[:2]),
                FORMATO_A_FORMULA.get(prod.get("formato_lote", ""), ""),
            )
            # Los lotes viejos (antes de la fabrica) son todos contradiccion local.
            if not formula and re.match(r"^20\d\d-\d\d-\d\d", lote.name):
                formula = "contradiccion local"

            fecha = prod.get("creado_lote") or datetime.fromtimestamp(
                mp4.stat().st_mtime
            ).strftime("%Y-%m-%d")

            portada = tipo_portada(lote, base)
            try:
                dt = datetime.strptime(fecha, "%Y-%m-%d")
                en_ventana = "si" if GANCHO_DESDE <= dt <= GANCHO_HASTA else "no"
            except ValueError:
                en_ventana = ""

            filas.append({
                "archivo": mp4.name,
                "lote": lote.name,
                "slug_guion": slug,
                "titulo": guion.get("titulo", ""),
                "formula": formula or "(sin clasificar)",
                "estado_mx": deducir_estado(
                    guion.get("etiqueta_mapa", ""),
                    guion.get("consulta_mapa", ""),
                    guion.get("hashtags", ""),
                    slug,
                ),
                "lugar": guion.get("etiqueta_mapa", ""),
                "portada": portada,
                "en_ventana_gancho": en_ventana,
                "fecha": fecha,
                "vigencia": prod.get("vigencia", ""),
                "estado_produccion": prod.get("estado_produccion", ""),
                "texto_portada": guion.get("texto_portada", ""),
                "n_planos": guion.get("n_planos", ""),
                "n_evidencia": guion.get("n_evidencia", ""),
                "mp4_mb": round(mp4.stat().st_size / 1_048_576, 1),
                # Se llenan desde el export de TikTok Studio:
                "vistas": "", "likes": "", "comentarios": "", "compartidos": "",
                "guardados": "", "tiempo_visto_seg": "", "pct_completado": "",
                "publicado": "",
            })

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8-sig") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"{len(filas)} videos -> {SALIDA}")

    # Resumen rapido en consola.
    def resumir(campo: str) -> None:
        conteo: dict[str, int] = {}
        for f in filas:
            conteo[f[campo] or "(vacio)"] = conteo.get(f[campo] or "(vacio)", 0) + 1
        orden = sorted(conteo.items(), key=lambda kv: -kv[1])
        print(f"\n{campo}:")
        for k, v in orden[:12]:
            print(f"  {v:4d}  {k}")

    for campo in ("formula", "portada", "estado_mx", "vigencia"):
        resumir(campo)

    con_guion = sum(1 for f in filas if f["slug_guion"])
    print(f"\namarrados a su guion: {con_guion}/{len(filas)}")


if __name__ == "__main__":
    main()
