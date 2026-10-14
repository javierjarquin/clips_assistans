"""Arma la evidencia del video de Tierra Blanca y la asigna a cada plano.

Sale del POC de evidencia (tools/evidencia_poc.py) más tres tipos de pieza:
  - la portada de la Recomendación 5VG/2017 de la CNDH (texto administrativo,
    LFDA art. 14 fracc. VIII),
  - la foto de Javier Duarte en Wikimedia (licencia libre),
  - fichas de texto con un dato y su fuente: no son imágenes de IA ni fotos
    de nadie, son el dato escrito (la salida que el CLAUDE.md del narrador ya
    daba para "no hay foto real").

Deja todo en C:\\Android_in\\<slug>\\imagenes_manuales\\<plano>_1_<n>.jpg, que
el bot copia como media/<plano>/elegido_<n> (ver pipeline._apply_manual_images).

    .venv\\Scripts\\python.exe tools\\evidencia_tierra_blanca.py
"""

import json
import sys
from itertools import cycle, islice
from pathlib import Path

import fitz  # PyMuPDF
import requests
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SLUG = "guion-tierra-blanca-evidencia"
POC = Path(__file__).resolve().parents[1] / "analisis" / "evidencia_tierra_blanca"
PIEZAS = POC / "piezas_video"
MANUALES = Path(r"C:\Android_in") / SLUG / "imagenes_manuales"
UA = {"User-Agent": "DatoMataGato-evidencia/0.1 (javier.jarquin.chooc@gmail.com)"}
FONDO, AMARILLO, BLANCO, GRIS = (14, 14, 16), (235, 200, 60), (240, 240, 240), (150, 150, 150)
TOMAS_POR_PLANO = 5  # de sobra: el narrador pide entre 1 y 4 según el largo
MARGEN = 170  # zona segura a cada lado: el movimiento de cámara recorta los bordes


def _fuente(tam: int, negrita: bool = True):
    try:
        return ImageFont.truetype("arialbd.ttf" if negrita else "arial.ttf", tam)
    except OSError:
        return ImageFont.load_default()


def _envolver(d, texto, fuente, ancho):
    lineas, linea = [], ""
    for palabra in texto.split():
        prueba = (linea + " " + palabra).strip()
        if d.textlength(prueba, font=fuente) > ancho and linea:
            lineas.append(linea)
            linea = palabra
        else:
            linea = prueba
    return lineas + [linea] if linea else lineas


def ficha(nombre: str, titulo: str, renglones: list[str], fuente: str) -> Path:
    """Un dato escrito, con su fuente. Nada de fotos de personas."""
    im = Image.new("RGB", (1080, 1920), FONDO)
    d = ImageDraw.Draw(im)
    # Margen de 170 px por lado: el movimiento de cámara del narrador recorta
    # los costados, y en el primer render se comía el final de cada renglón.
    x, ancho, y = MARGEN, 1080 - 2 * MARGEN, 600
    for linea in _envolver(d, titulo.upper(), _fuente(72), ancho):
        d.text((x, y), linea, fill=AMARILLO, font=_fuente(72))
        y += 86
    y += 30
    d.line([(x, y), (x + ancho, y)], fill=AMARILLO, width=4)
    y += 50
    for r in renglones:
        for linea in _envolver(d, r, _fuente(46, False), ancho):
            d.text((x, y), linea, fill=BLANCO, font=_fuente(46, False))
            y += 60
        y += 22
    for linea in _envolver(d, f"FUENTE: {fuente.upper()}", _fuente(30), ancho):
        d.text((x, y + 40), linea, fill=GRIS, font=_fuente(30))
        y += 40
    ruta = PIEZAS / f"ficha_{nombre}.jpg"
    im.save(ruta, quality=92)
    return ruta


def portada_cndh() -> Path:
    pdf = POC / "RecVG_005.pdf"
    if not pdf.exists():
        pdf.write_bytes(requests.get(
            "https://www.cndh.org.mx/sites/default/files/doc/Recomendaciones/"
            "ViolacionesGraves/RecVG_005.pdf", headers=UA, timeout=120).content)
    doc = fitz.open(pdf)
    pag = doc[0]
    png = pag.get_pixmap(dpi=150, clip=fitz.Rect(0, 0, pag.rect.width, pag.rect.height * 0.55))
    crudo = POC / "_cndh_p1.png"
    png.save(crudo)
    hoja = Image.open(crudo).convert("RGB")
    ancho = 1080 - 2 * MARGEN
    hoja = hoja.resize((ancho, round(hoja.height * ancho / hoja.width)), Image.LANCZOS)
    im = Image.new("RGB", (1080, 1920), FONDO)
    y = (1920 - hoja.height) // 2 - 60
    im.paste(hoja, (MARGEN, y))
    ImageDraw.Draw(im).text((MARGEN, y + hoja.height + 40), "FUENTE: CNDH · REC. 5VG/2017",
                            fill=AMARILLO, font=_fuente(32))
    ruta = PIEZAS / "documento_cndh_5vg_portada.jpg"
    im.save(ruta, quality=92)
    print("CNDH: portada de", len(doc), "páginas")
    return ruta


def foto_wikimedia(titulo: str, nombre: str) -> Path:
    api = "https://commons.wikimedia.org/w/api.php"
    info = requests.get(api, headers=UA, timeout=30, params={
        "action": "query", "titles": titulo, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": 1080, "format": "json"}).json()
    ii = next(iter(info["query"]["pages"].values()))["imageinfo"][0]
    lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
    ruta = PIEZAS / f"persona_{nombre}.jpg"
    ruta.write_bytes(requests.get(ii["thumburl"], headers=UA, timeout=60).content)
    Image.open(ruta).convert("RGB").save(ruta, quality=92)
    print(f"Wikimedia: {titulo} | {lic}")
    return ruta


def main() -> None:
    PIEZAS.mkdir(parents=True, exist_ok=True)
    MANUALES.mkdir(parents=True, exist_ok=True)
    for viejo in MANUALES.glob("*"):
        viejo.unlink()

    lugar = {p.stem.split("_", 1)[1].split("_")[0].lower(): p for p in POC.glob("lugar_*.jpg")}
    silla = POC / "prensa_silla_rota_2026.png"
    pie = POC / "prensa_pie_de_pagina_7_anos.png"
    disculpa = POC / "documento_cndh_disculpa.png"

    hoy = ficha("hoy", "10 años · 20 detenidos · 0 sentencias",
                ["Enero de 2016: cinco jóvenes de Playa Vicente detenidos por la Policía "
                 "Estatal en Tierra Blanca, Veracruz.",
                 "Enero de 2026: ninguna sentencia."], "La Silla Rota, 12/01/2026")
    victimas = ficha("victimas", "Detenidos el 11 de enero de 2016",
                     ["José Benítez de la O", "Bernardo Benítez Arroniz",
                      "José Alfredo González Díaz", "Mario Arturo Orozco Sánchez",
                      "Una adolescente de 16 años"],
                     # La CNDH los anonimiza (V1..V4, MV): los nombres son de la prensa.
                     "Pie de Página")
    h1137 = ficha("1137", "11:37 · Tierra Blanca",
                  ["Una cámara de seguridad cerca de un Chedraui graba a policías "
                   "estatales deteniendo un Jetta blanco."], "Milenio, cronología del caso")
    h1221 = ficha("1221", "12:21 · En la camioneta",
                  ["La cámara muestra a los jóvenes arriba de una camioneta de la policía.",
                   "21:00 · El Jetta aparece abandonado en Paso del Toro, Medellín, a más "
                   "de 70 km."], "Milenio, cronología del caso")
    detenidos = ficha("detenidos", "Detenidos, sin sentencia",
                      ["14/01/2016 · Cuatro policías estatales. Aceptaron la detención; "
                       "dijeron no saber dónde estaban los jóvenes.",
                       "17/01/2016 · Marcos Conde Hernández, delegado de Seguridad Pública "
                       "en Tierra Blanca."], "Milenio, cronología del caso")
    fiscal = ficha("fiscal", "20/01/2016 · El fiscal Luis Ángel Bravo",
                   ["Un testigo afirmó que los policías entregaron a los jóvenes al "
                    "crimen organizado."], "Milenio, cronología del caso")
    rancho = ficha("rancho", "Rancho El Limón · Tlalixcoyan",
                   ["Restos de unas 300 personas.",
                    "Entre ellos, un fragmento de hueso de Bernardo Benítez."],
                   "Pie de Página")
    cndh = portada_cndh()
    duarte = foto_wikimedia("File:Javier Duarte de Ochoa.jpg", "javier_duarte")

    asignacion = {
        "p00": [silla, hoy, pie],
        "p01": [victimas, lugar.get("mexico"), lugar.get("central")],
        "p02": [lugar.get("central"), h1137, lugar.get("iglesia"), lugar.get("glorieta")],
        "p03": [h1221, lugar.get("glorieta"), lugar.get("iglesia")],
        "p04": [detenidos, lugar.get("palacio")],
        "p05": [duarte, fiscal],
        "p06": [rancho, cndh, disculpa],
        "p07": [silla, hoy, pie],
    }
    registro = {}
    for plano, piezas in asignacion.items():
        piezas = [p for p in piezas if p is not None and Path(p).exists()]
        registro[plano] = []
        for n, pieza in enumerate(islice(cycle(piezas), TOMAS_POR_PLANO), start=1):
            destino = MANUALES / f"{plano}_1_{n}.jpg"
            Image.open(pieza).convert("RGB").save(destino, quality=92)
            registro[plano].append(Path(pieza).name)
    (POC / "asignacion.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    for plano, nombres in registro.items():
        print(plano, "->", ", ".join(dict.fromkeys(nombres)))


if __name__ == "__main__":
    main()
