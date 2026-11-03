"""Empalma el export de TikTok Studio con el inventario local.

El export es la lista autoritativa: el disco tiene 328 videos pero Javier
publica a mano, asi que solo TikTok sabe cuales salieron. Por eso el empalme
va del export hacia el inventario, y no al reves.

Uso:
    python tools/empalmar_tiktok.py <export_de_tiktok.csv>

Salida:
    analisis/formula_vs_metricas.csv   una fila por video publicado
    analisis/sin_empalmar.csv          lo que no amarro, para revisar a mano

Las columnas del export cambian segun idioma y version, asi que se detectan
por alias en vez de por posicion.
"""

from __future__ import annotations

import csv
import difflib
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INVENTARIO = RAIZ / "analisis" / "inventario_videos.csv"
SALIDA = RAIZ / "analisis" / "formula_vs_metricas.csv"
HUERFANOS = RAIZ / "analisis" / "sin_empalmar.csv"

ALIAS = {
    "titulo": ["video title", "titulo del video", "título del video", "title",
               "descripcion", "descripción", "description", "video description"],
    "fecha": ["date posted", "post time", "fecha de publicacion",
              "fecha de publicación", "create time", "fecha"],
    "vistas": ["video views", "views", "vistas del video", "vistas",
               "reproducciones"],
    "likes": ["likes", "me gusta", "corazones"],
    "comentarios": ["comments", "comentarios"],
    "compartidos": ["shares", "compartidos", "veces compartido"],
    "guardados": ["saves", "guardados", "favoritos", "bookmarks"],
    "tiempo_visto_seg": ["average watch time", "tiempo promedio de visualizacion",
                         "tiempo promedio de visualización", "avg watch time"],
    "pct_completado": ["watched full video", "video completo", "retencion",
                       "retención", "completion rate", "porcentaje de visualizacion"],
}


def plano(texto: str) -> str:
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto or "")
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]", "", sin_acentos.lower())


def sin_hashtags(texto: str) -> str:
    return re.sub(r"#\w+", " ", texto or "")


def mapear_columnas(encabezados: list[str]) -> dict[str, str]:
    """Campo nuestro -> nombre real de la columna en el export."""
    mapa: dict[str, str] = {}
    normalizados = {h.strip().lower(): h for h in encabezados}
    for campo, alias in ALIAS.items():
        for a in alias:
            if a in normalizados:
                mapa[campo] = normalizados[a]
                break
        else:
            # Segundo intento: que el encabezado contenga el alias.
            for bajo, real in normalizados.items():
                if any(a in bajo for a in alias):
                    mapa[campo] = real
                    break
    return mapa


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nFalta la ruta del export de TikTok Studio.")
        sys.exit(1)

    export = Path(sys.argv[1])
    if not export.exists():
        print(f"No existe: {export}")
        sys.exit(1)

    inventario = list(csv.DictReader(INVENTARIO.open(encoding="utf-8-sig")))
    # Indice por titulo normalizado, para buscar por parecido.
    indice = {plano(f["titulo"]): f for f in inventario if f["titulo"]}
    claves = list(indice)

    with export.open(encoding="utf-8-sig", newline="") as fh:
        publicados = list(csv.DictReader(fh))
    if not publicados:
        print("El export vino vacio.")
        sys.exit(1)

    mapa = mapear_columnas(list(publicados[0].keys()))
    print("Columnas detectadas en el export:")
    for campo in ALIAS:
        print(f"  {campo:18s} -> {mapa.get(campo, '(no encontrada)')}")
    if "titulo" not in mapa:
        print("\nSin columna de titulo no se puede empalmar. Revisa el export.")
        sys.exit(1)
    print()

    filas, huerfanos = [], []
    usados: set[str] = set()

    for pub in publicados:
        titulo_tt = (pub.get(mapa["titulo"]) or "").strip()
        buscado = plano(sin_hashtags(titulo_tt))
        local = None

        if buscado in indice:
            local = indice[buscado]
        else:
            # El titulo de TikTok suele traer la descripcion completa:
            # primero por contencion, luego por parecido.
            contenidos = [k for k in claves if k and (k in buscado or buscado in k)]
            if contenidos:
                local = indice[max(contenidos, key=len)]
            else:
                cerca = difflib.get_close_matches(buscado, claves, n=1, cutoff=0.78)
                if cerca:
                    local = indice[cerca[0]]

        metricas = {
            nuestro: (pub.get(mapa[nuestro], "") if nuestro in mapa else "")
            for nuestro in ("vistas", "likes", "comentarios", "compartidos",
                            "guardados", "tiempo_visto_seg", "pct_completado")
        }
        fecha_tt = pub.get(mapa.get("fecha", ""), "")

        if local is None:
            huerfanos.append({"titulo_tiktok": titulo_tt,
                              "fecha_tiktok": fecha_tt, **metricas})
            continue

        usados.add(plano(local["titulo"]))
        fila = dict(local)
        fila.update(metricas)
        fila["publicado"] = "si"
        fila["titulo_tiktok"] = titulo_tt
        fila["fecha_tiktok"] = fecha_tt
        filas.append(fila)

    if filas:
        campos = list(filas[0].keys())
        with SALIDA.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            w.writerows(filas)
        print(f"empalmados: {len(filas)} -> {SALIDA}")

    if huerfanos:
        with HUERFANOS.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(huerfanos[0].keys()))
            w.writeheader()
            w.writerows(huerfanos)
        print(f"sin empalmar: {len(huerfanos)} -> {HUERFANOS}")

    nunca = len(indice) - len(usados)
    print(f"en disco y nunca publicados (o sin empalme): {nunca}")
    print("\nSiguiente paso: python tools/resumir_formula.py")


if __name__ == "__main__":
    main()
