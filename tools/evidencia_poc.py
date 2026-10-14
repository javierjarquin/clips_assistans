"""POC: cómo se consigue evidencia digital REAL de un caso, sin IA.

Tres tipos de pieza, cada una con su fuente y su base para poder usarla:

  lugar      fotos del sitio en Wikimedia Commons (licencia libre, con autor)
  documento  captura de un texto oficial (CNDH, fiscalía, sentencia). La LFDA,
             art. 14 fracc. VIII, deja fuera de protección los textos
             administrativos y judiciales.
  prensa     captura del TITULAR y la fecha de una nota ("así lo publicó...").
             Es cita (LFDA art. 148 fracc. I), con la fuente en pantalla. Riesgo
             medio: no se captura la foto de la nota, solo el titular.

Salida: analisis/evidencia_<caso>/ con las piezas, manifest.json y una hoja de
contacto para revisar.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\evidencia_poc.py
"""

import json
import re
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CASO = "tierra_blanca"
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / f"evidencia_{CASO}"
UA = {"User-Agent": "DatoMataGato-evidencia/0.1 (javier.jarquin.chooc@gmail.com)"}

# Lo que salió de investigar el caso (28/09/2026), con su fuente.
LUGAR = {"categoria": "Category:Tierra_Blanca_Municipality",
         "quiero": ["palacio", "central", "location map", "glorieta", "iglesia"]}
CAPTURAS = [
    ("documento", "cndh_recomendacion",
     "https://www.cndh.org.mx/documento/emite-cndh-recomendacion-por-violaciones-graves-derechos-humanos-al-gobierno-de-veracruz",
     "CNDH, Recomendación 5VG/2017 (19/07/2017)"),
    ("documento", "cndh_disculpa",
     "https://hist.cndh.org.mx/documento/reconocimiento-de-responsabilidad-y-disculpa-publica-del-gobierno-del-estado-de-veracruz",
     "CNDH: disculpa pública del Gobierno de Veracruz"),
    ("prensa", "proceso_exonero",
     "https://www.proceso.com.mx/nacional/2019/3/15/urgen-la-fgr-que-combata-sentencia-que-exonero-21-por-la-desaparicion-de-cinco-jovenes-en-tierra-blanca-221746.html",
     "Proceso, 15/03/2019"),
    ("prensa", "silla_rota_2026",
     "https://lasillarota.com/veracruz/estado/2026/1/12/ya-estamos-cansados-que-sentencien-responsables-jose-benitez-por-caso-tierra-blanca-490517.html",
     "La Silla Rota, 12/01/2026"),
    ("prensa", "pie_de_pagina_7_anos",
     "https://piedepagina.mx/tres-gobernadores-y-7-anos-sin-sentencias-por-jovenes-desaparecidos-en-tierra-blanca/",
     "Pie de Página"),
]
BASE_LEGAL = {
    "lugar": "Wikimedia Commons, licencia libre (ver licencia y autor)",
    "documento": "LFDA art. 14 fracc. VIII: texto administrativo, sin derechos",
    "prensa": "LFDA art. 148 fracc. I: cita del titular con la fuente",
}


def wikimedia_del_lugar() -> list[dict]:
    api = "https://commons.wikimedia.org/w/api.php"
    miembros = requests.get(api, headers=UA, timeout=30, params={
        "action": "query", "list": "categorymembers", "cmtitle": LUGAR["categoria"],
        "cmtype": "file", "cmlimit": 200, "format": "json"}).json()["query"]["categorymembers"]
    elegidos = [m["title"] for m in miembros
                if any(q in m["title"].lower() for q in LUGAR["quiero"])][:6]
    piezas = []
    for titulo in elegidos:
        info = requests.get(api, headers=UA, timeout=30, params={
            "action": "query", "titles": titulo, "prop": "imageinfo",
            "iiprop": "url|extmetadata", "iiurlwidth": 1080, "format": "json"}).json()
        ii = next(iter(info["query"]["pages"].values()))["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        limpio = re.sub(r"[^\w-]+", "_", titulo.split(":", 1)[1].rsplit(".", 1)[0])[:50]
        destino = SALIDA / f"lugar_{limpio}.jpg"
        crudo = requests.get(ii.get("thumburl") or ii["url"], headers=UA, timeout=60).content
        destino.write_bytes(crudo)
        try:  # los SVG vienen como PNG en thumburl; lo normalizo a JPG
            Image.open(destino).convert("RGB").save(destino, quality=90)
        except Exception:  # noqa: BLE001
            pass
        piezas.append({
            "tipo": "lugar", "archivo": destino.name, "fuente": ii["descriptionurl"],
            "licencia": meta.get("LicenseShortName", {}).get("value", "?"),
            "autor": meta.get("Artist", {}).get("value", "?")[:120],
            "base": BASE_LEGAL["lugar"],
        })
        print("lugar:", titulo, "|", piezas[-1]["licencia"], flush=True)
    return piezas


def capturas() -> list[dict]:
    from playwright.sync_api import sync_playwright

    piezas = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        # Formato celular: la captura ya sale del ancho del video vertical.
        ctx = nav.new_context(viewport={"width": 430, "height": 760},
                              device_scale_factor=2.5, locale="es-MX",
                              user_agent=("Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
                                          "(KHTML, like Gecko) Chrome/151.0 Mobile Safari/537.36"))
        for tipo, nombre, url, etiqueta in CAPTURAS:
            pagina = ctx.new_page()
            try:
                pagina.goto(url, wait_until="domcontentloaded", timeout=45000)
                pagina.wait_for_timeout(3500)
                # Banners de cookies/suscripción: se intenta cerrar, no se insiste.
                for texto in ("Aceptar", "Acepto", "Entendido", "Cerrar", "No, gracias"):
                    try:
                        pagina.get_by_role("button", name=texto).first.click(timeout=800)
                    except Exception:  # noqa: BLE001
                        pass
                # SOLO el titular y lo que tiene justo debajo (fecha, autor):
                # la página entera trae anuncios y, en Pie de Página, las
                # fotos de las víctimas -- entre ellas una menor de edad.
                destino = SALIDA / f"{tipo}_{nombre}.png"
                h1 = pagina.locator("h1").first
                h1.scroll_into_view_if_needed(timeout=5000)
                caja = h1.bounding_box()
                arriba = max(0, caja["y"] - 30)
                # Corta antes de la primera imagen debajo del titular (foto de
                # la nota o anuncio), y nunca más de 110 px bajo el titular.
                img_top = pagina.evaluate(
                    """(fondo) => { const t = [...document.images]
                         .map(i => i.getBoundingClientRect())
                         .filter(r => r.top > fondo && r.width > 60 && r.height > 40)
                         .map(r => r.top); return t.length ? Math.min(...t) : null; }""",
                    caja["y"] + caja["height"])
                abajo = caja["y"] + caja["height"] + 110
                if img_top is not None:
                    abajo = min(abajo, img_top - 6)
                pagina.screenshot(path=str(destino), clip={
                    "x": 0, "y": arriba, "width": 430, "height": abajo - arriba})
                tarjeta(destino, etiqueta)
                piezas.append({"tipo": tipo, "archivo": destino.name, "fuente": url,
                               "etiqueta": etiqueta, "base": BASE_LEGAL[tipo]})
                print(tipo + ":", etiqueta, flush=True)
            except Exception as exc:  # noqa: BLE001
                print(f"{tipo}: {etiqueta} FALLÓ ({exc})", flush=True)
            finally:
                pagina.close()
        nav.close()
    return piezas


def tarjeta(captura: Path, fuente: str) -> None:
    """La captura montada como toma vertical: el recorte al centro sobre fondo
    oscuro y la fuente escrita abajo. Pisa el archivo de la captura."""
    # 170 px de margen por lado: el movimiento de cámara del narrador recorta
    # los costados (primer render de Tierra Blanca, 28/09/2026).
    margen = 170
    ancho = 1080 - 2 * margen
    im = Image.open(captura).convert("RGB")
    im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    lienzo = Image.new("RGB", (1080, 1920), (14, 14, 16))
    y = (1920 - im.height) // 2 - 60
    lienzo.paste(im, (margen, y))
    d = ImageDraw.Draw(lienzo)
    try:
        f = ImageFont.truetype("arialbd.ttf", 30)
    except OSError:
        f = ImageFont.load_default()
    # La fuente pasa a otra línea si no entra: "CNDH: disculpa pública del
    # Gobierno de Veracruz" se cortaba en el borde de la tarjeta.
    lineas, linea = [], ""
    for palabra in f"FUENTE: {fuente.upper()}".split():
        prueba = (linea + " " + palabra).strip()
        if d.textlength(prueba, font=f) > ancho and linea:
            lineas.append(linea)
            linea = palabra
        else:
            linea = prueba
    for i, texto in enumerate(lineas + [linea]):
        d.text((margen, y + im.height + 36 + i * 40), texto, fill=(235, 200, 60), font=f)
    lienzo.save(captura)


def hoja_de_contacto(piezas: list[dict]) -> Path:
    lado, cols = 300, 4
    filas = (len(piezas) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * lado, filas * (lado + 40)), (20, 20, 20))
    d = ImageDraw.Draw(hoja)
    try:
        fuente = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        fuente = ImageFont.load_default()
    for i, p in enumerate(piezas):
        im = Image.open(SALIDA / p["archivo"]).convert("RGB")
        im.thumbnail((lado, lado))
        x, y = (i % cols) * lado, (i // cols) * (lado + 40)
        hoja.paste(im, (x + (lado - im.width) // 2, y))
        d.text((x + 6, y + lado + 8), f"{p['tipo'].upper()}: {p['archivo'][:28]}",
               fill=(230, 200, 60), font=fuente)
    ruta = SALIDA / "_hoja.jpg"
    hoja.save(ruta, quality=85)
    return ruta


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    piezas = wikimedia_del_lugar() + capturas()
    (SALIDA / "manifest.json").write_text(json.dumps(piezas, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(f"\n{len(piezas)} piezas -> {SALIDA}")
    print("hoja:", hoja_de_contacto(piezas))


if __name__ == "__main__":
    main()
