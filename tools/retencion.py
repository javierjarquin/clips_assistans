"""Retención por formato: qué video es de qué formato y cómo le fue (22/11/2026).

La prueba de un mes con los 8 formatos (desde el 06/11/2026) no tenía con qué
medirse: `analisis/retencion_tiktok/registro.csv` estaba vacío. Esto liga cada
video archivado con su guion y su formato, mete las métricas de TikTok Studio y
saca la mediana por formato.

    python tools/retencion.py inventario
        Cada mp4 de C:\\Android_in\\lotes\\ con su slug, formato, título y duración
        -> analisis/retencion_tiktok/inventario.csv

    python tools/retencion.py importar <exportacion.csv|.xlsx>
        La exportación de TikTok Studio (Analíticas > Contenido > descargar). Cada
        fila se liga a un video del inventario por el título/descripción, y se
        agrega o actualiza en registro.csv. Lo que no se pudo ligar se lista.

    python tools/retencion.py reporte
        Mediana por formato de vistas, segundos vistos, % de retención (segundos
        vistos / duración), % visto completo y comentarios
        -> analisis/retencion_tiktok/reporte_formatos.md

registro.csv también se puede llenar a mano (una fila por video); `reporte` lee
lo que haya. La columna fyf_no_apto es "si" cuando TikTok avisa que el video no
es apto para el For You (reglas del 24/09/2026), para ver si un formato lo sufre.
"""

import csv
import json
import re
import statistics
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ANDROID_IN = Path(r"C:\Android_in")
AQUI = Path(__file__).resolve().parents[1] / "analisis" / "retencion_tiktok"
INVENTARIO = AQUI / "inventario.csv"
REGISTRO = AQUI / "registro.csv"
REPORTE = AQUI / "reporte_formatos.md"

COLUMNAS_INVENTARIO = ("archivo", "lote", "slug", "formato", "titulo", "duracion_seg")
COLUMNAS_REGISTRO = ("fecha_publicacion", "archivo", "slug", "formula", "duracion_seg", "vistas_48h",
                     "vistas", "tiempo_promedio_seg", "pct_visto_completo", "segundo_de_la_caida", "comentarios",
                     "compartidos", "fyf_no_apto", "titulo_tiktok", "notas")

# El formato sale del estado del lote; si el lote es de antes, del prefijo del slug.
PREFIJOS = (("guion-viral-", "viral"), ("guion-polemica-", "polemica"), ("guion-tradicion-", "tradiciones"),
            ("guion-notedicen-", "notedicen"), ("guion-comparativa-", "comparativa"), ("guion-serie-", "serie"),
            ("guion-caso-", "caso"), ("guion-papasia-", "papasia"), ("mito-", "mito"))


# ------------------------------------------------------------------- utilidades

def normal(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto or "")).lower()
    return "".join(c for c in t if not unicodedata.combining(c))


def slugify_titulo(titulo: str) -> str:
    """El nombre del mp4 archivado (igual que drive_upload.slugify_titulo del bot)."""
    return "".join(re.findall(r"[a-z0-9]+", normal(titulo))) or "video"


def palabras(texto: str) -> set[str]:
    return {p for p in re.findall(r"[a-z0-9]+", normal(texto)) if len(p) > 2}


def duracion(mp4: Path) -> float | None:
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(mp4)], capture_output=True, text=True, timeout=30)
        return round(float(r.stdout.strip()), 1)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def leer_csv(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def escribir_csv(ruta: Path, columnas, filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def _guion(slug: str) -> dict:
    for base in (ANDROID_IN, ANDROID_IN / "papasia"):
        ruta = base / slug / "guion.json"
        if ruta.exists():
            try:
                g = json.loads(ruta.read_text(encoding="utf-8"))
                return g if isinstance(g, dict) else {}
            except (OSError, ValueError):
                return {}
    return {}


def _titulo(g: dict, slug: str) -> str:
    return str(g.get("titulo") or (g.get("meta") or {}).get("titulo") or slug).strip()


def formato_de(slug: str, del_estado: str | None, formato_lote: str | None) -> str:
    if del_estado:
        return del_estado
    for prefijo, formato in PREFIJOS:
        if slug.startswith(prefijo):
            return formato
    if formato_lote in ("cercania", "crimen", "redes"):
        return formato_lote
    return "clasico"  # true crime de antes de los formatos (guion-<caso>)


# ------------------------------------------------------------------- inventario

def _todos_los_guiones() -> dict[str, list[str]]:
    """nombre de mp4 esperado -> slugs, de TODOS los guiones (para los lotes viejos
    que no tienen estado.json en la fábrica)."""
    indice: dict[str, list[str]] = {}
    for base in (ANDROID_IN, ANDROID_IN / "papasia"):
        for ruta in base.glob("*/guion.json"):
            slug = ruta.parent.name
            indice.setdefault(slugify_titulo(_titulo(_guion(slug), slug)), []).append(slug)
    return indice


def inventario() -> list[dict]:
    """Cada mp4 archivado con su slug y formato. El nombre del mp4 es el título
    del guion pasado por slugify (con _2, _3 si se repite)."""
    filas = []
    global_ = _todos_los_guiones()
    for base in (ANDROID_IN, ANDROID_IN / "papasia"):
        for carpeta in sorted((base / "lotes").glob("*")):
            if not carpeta.is_dir():
                continue
            estado_ruta = base / "fabrica" / carpeta.name / "estado.json"
            estado = json.loads(estado_ruta.read_text(encoding="utf-8")) if estado_ruta.exists() else {}
            # nombre esperado del mp4 -> slug, con los slugs del estado del lote
            por_nombre: dict[str, list[str]] = {}
            for slug in (estado.get("videos") or {}):
                por_nombre.setdefault(slugify_titulo(_titulo(_guion(slug), slug)), []).append(slug)
            for mp4 in sorted(carpeta.glob("*.mp4")):
                if mp4.stem.endswith("_telegram"):
                    continue
                nombre = re.sub(r"_\d+$", "", mp4.stem)
                candidatos = por_nombre.get(nombre) or []
                slug = candidatos.pop(0) if candidatos else ""
                if not slug and len(global_.get(nombre) or []) == 1:
                    slug = global_[nombre][0]   # lote viejo: el único guion con ese título
                v = (estado.get("videos") or {}).get(slug, {})
                filas.append({"archivo": mp4.name, "lote": carpeta.name, "slug": slug,
                              "formato": formato_de(slug, v.get("formato"), estado.get("formato")) if slug
                              else ("papasia" if base.name == "papasia" else "sin_guion"),
                              "titulo": _titulo(_guion(slug), slug) if slug else "",
                              "duracion_seg": duracion(mp4) or ""})
    escribir_csv(INVENTARIO, COLUMNAS_INVENTARIO, filas)
    return filas


# --------------------------------------------------------- exportación de Studio

# Nombres de columna posibles (español e inglés), ya normalizados. Se busca que
# el encabezado CONTENGA alguno: TikTok cambia el texto exacto entre versiones.
ALIAS = {
    "titulo_tiktok": ("video title", "titulo del video", "titulo", "descripcion", "description", "caption"),
    "fecha_publicacion": ("post time", "posted", "fecha de publicacion", "hora de publicacion", "publicado", "date"),
    "vistas": ("video views", "visualizaciones", "reproducciones", "vistas", "views"),
    "tiempo_promedio_seg": ("average watch time", "tiempo de reproduccion promedio", "tiempo medio",
                            "tiempo promedio", "avg. watch time"),
    "pct_visto_completo": ("watched full video", "full video views", "visto completo", "video completo",
                           "vio el video completo", "completion"),
    "comentarios": ("comments", "comentarios"),
    "compartidos": ("shares", "compartido", "compartidos"),
    "duracion_seg": ("duration", "duracion"),
}


def _leer_exportacion(ruta: Path) -> list[dict]:
    if ruta.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("Para .xlsx hace falta openpyxl (pip install openpyxl) o exporta como CSV.")
        hoja = openpyxl.load_workbook(ruta, read_only=True, data_only=True).active
        filas = list(hoja.iter_rows(values_only=True))
        encabezado = [str(c or "") for c in filas[0]]
        return [dict(zip(encabezado, f)) for f in filas[1:] if any(c is not None for c in f)]
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def mapear_columnas(encabezados: list[str]) -> dict[str, str]:
    """{campo del registro: encabezado de la exportación}."""
    mapa = {}
    for campo, alias in ALIAS.items():
        for h in encabezados:
            if any(a in normal(h) for a in alias) and h not in mapa.values():
                mapa[campo] = h
                break
    return mapa


def _numero(valor) -> str:
    """'1,234' -> '1234'; '45.3%' -> '45.3'; '12s' -> '12'; '1:05' -> '65'; '1.2K' -> '1200'."""
    t = str(valor or "").strip().lower().replace("%", "").replace("s", "").strip()
    if not t:
        return ""
    if re.fullmatch(r"\d+:\d{2}", t):
        m, s = t.split(":")
        return str(int(m) * 60 + int(s))
    mult = 1000 if t.endswith("k") else 10**6 if t.endswith("m") else 1
    t = t.rstrip("km").replace(",", "") if "," in t and "." not in t else t.rstrip("km").replace(",", "")
    try:
        n = float(t) * mult
    except ValueError:
        return ""
    return str(int(n)) if n.is_integer() else str(round(n, 2))


def ligar(texto: str, inventario_filas: list[dict]) -> dict | None:
    """El video del inventario cuyo título se parece más al texto de TikTok
    (Javier publica con el título y la descripción que da la fábrica)."""
    buscadas = palabras(texto)
    mejor, puntaje = None, 0.0
    for fila in inventario_filas:
        suyas = palabras(fila["titulo"]) or palabras(fila["archivo"])
        if not suyas:
            continue
        p = len(buscadas & suyas) / len(suyas)
        if p > puntaje:
            mejor, puntaje = fila, p
    return mejor if puntaje >= 0.6 else None


def importar(ruta: Path) -> None:
    filas = _leer_exportacion(ruta)
    if not filas:
        sys.exit(f"{ruta} no tiene filas.")
    mapa = mapear_columnas(list(filas[0].keys()))
    print("Columnas reconocidas:")
    for campo in ALIAS:
        print(f"  {campo:22} <- {mapa.get(campo, '(no está)')}")
    sin_usar = [h for h in filas[0] if h not in mapa.values()]
    if sin_usar:
        print("Columnas que no reconocí (si alguna sirve, agrégala a ALIAS):", ", ".join(sin_usar))
    if "titulo_tiktok" not in mapa:
        sys.exit("Sin columna de título/descripción no puedo ligar los videos con su formato.")
    inv = leer_csv(INVENTARIO) or inventario()
    registro = {r["archivo"] or r.get("titulo_tiktok", ""): r for r in leer_csv(REGISTRO)}
    nuevas, actualizadas, sueltas = 0, 0, []
    for fila in filas:
        texto = str(fila.get(mapa["titulo_tiktok"]) or "")
        video = ligar(texto, inv)
        if video is None:
            sueltas.append(texto[:80])
            continue
        r = registro.get(video["archivo"]) or {"archivo": video["archivo"]}
        actualizadas += video["archivo"] in registro
        nuevas += video["archivo"] not in registro
        r.update({"slug": video["slug"], "formula": video["formato"],
                  "duracion_seg": r.get("duracion_seg") or video["duracion_seg"], "titulo_tiktok": texto[:120]})
        for campo in ("vistas", "tiempo_promedio_seg", "pct_visto_completo", "comentarios", "compartidos"):
            if campo in mapa:
                r[campo] = _numero(fila.get(mapa[campo]))
        if "fecha_publicacion" in mapa:
            r["fecha_publicacion"] = str(fila.get(mapa["fecha_publicacion"]) or "")[:16]
        registro[video["archivo"]] = r
    escribir_csv(REGISTRO, COLUMNAS_REGISTRO, list(registro.values()))
    print(f"\n{nuevas} videos nuevos y {actualizadas} actualizados en {REGISTRO}")
    if sueltas:
        print(f"{len(sueltas)} filas sin ligar (no se parecen a ningún título del inventario):")
        for s in sueltas[:20]:
            print("  -", s)


# --------------------------------------------------------------------- reporte

def _mediana(valores: list[float]) -> str:
    return f"{statistics.median(valores):.1f}" if valores else "—"


def _num(x) -> float | None:
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def reporte() -> str:
    filas = leer_csv(REGISTRO)
    por_formato: dict[str, list[dict]] = {}
    for r in filas:
        por_formato.setdefault(r.get("formula") or "sin formato", []).append(r)
    lineas = [f"# Retención por formato ({datetime.now():%d/%m/%Y})", "",
              f"Fuente: `{REGISTRO.name}` ({len(filas)} videos). Medianas; retención = segundos vistos / "
              "duración. Con menos de 3 videos un formato no dice nada todavía.", "",
              "| Formato | Videos | Vistas | Seg. vistos | Retención % | % completo | Comentarios | No aptos FYF |",
              "|---|---|---|---|---|---|---|---|"]
    for formato, rs in sorted(por_formato.items(), key=lambda kv: -len(kv[1])):
        vistas = [v for r in rs if (v := _num(r.get("vistas") or r.get("vistas_48h"))) is not None]
        seg = [v for r in rs if (v := _num(r.get("tiempo_promedio_seg"))) is not None]
        ret = [100 * s / d for r in rs if (s := _num(r.get("tiempo_promedio_seg"))) is not None
               and (d := _num(r.get("duracion_seg")))]
        completo = [v for r in rs if (v := _num(r.get("pct_visto_completo"))) is not None]
        com = [v for r in rs if (v := _num(r.get("comentarios"))) is not None]
        no_aptos = sum(normal(r.get("fyf_no_apto")) in ("si", "1", "true") for r in rs)
        lineas.append(f"| {formato} | {len(rs)} | {_mediana(vistas)} | {_mediana(seg)} | {_mediana(ret)} | "
                      f"{_mediana(completo)} | {_mediana(com)} | {no_aptos} |")
    if not filas:
        lineas += ["", "Sin datos todavía: corre `importar` con la exportación de TikTok Studio o llena "
                   "registro.csv a mano."]
    texto = "\n".join(lineas) + "\n"
    REPORTE.write_text(texto, encoding="utf-8")
    return texto


def main(argv: list[str]) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not argv or argv[0] not in ("inventario", "importar", "reporte"):
        sys.exit(__doc__)
    if argv[0] == "inventario":
        filas = inventario()
        conteo: dict[str, int] = {}
        for f in filas:
            conteo[f["formato"]] = conteo.get(f["formato"], 0) + 1
        print(f"{len(filas)} videos -> {INVENTARIO}")
        for k, n in sorted(conteo.items(), key=lambda kv: -kv[1]):
            print(f"  {k:14} {n}")
    elif argv[0] == "importar":
        if len(argv) < 2:
            sys.exit("Uso: python tools/retencion.py importar <exportacion.csv|.xlsx>")
        importar(Path(argv[1]))
    else:
        print(reporte())


if __name__ == "__main__":
    main(sys.argv[1:])
