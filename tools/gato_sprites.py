"""Genera los sprites de boca del gato de Dato Mata Gato -- SUELTO, fuera del pipeline.

Parte del LOGO del canal (no de una IA) para que el personaje sea exactamente
el de la marca, y dibuja encima las 9 formas de boca que usa Rhubarb Lip Sync
(A-H mas X de reposo). Asi no hay deriva de diseno entre sprites: el cuerpo es
siempre el mismo pixel del logo, solo cambia la boca.

    python tools/gato_sprites.py --modo busto --out analisis/mascota_gato/sprites

Tres encuadres, para comparar cual funciona mejor en la esquina:

    cabeza   solo la cabeza, recortada, sin fondo
    busto    cabeza + cuello + pata + hombros, recortado, sin fondo
    emblema  la insignia circular completa (gato, libro y fondo azul del logo)

Por que existe `emblema`: el logo dibuja los contornos y las rayas del pelaje en
el MISMO azul marino del fondo, asi que recortar la silueta por color siempre
come pedazos del cuerpo (la corbata, sobre todo). En modo emblema no hay nada
que recortar -- el fondo del logo es parte del diseno.

Las formas siguen la convencion de Rhubarb:
    A cerrada (P/B/M)      B dientes juntos (EE)   C abierta (EH)
    D bien abierta (AA)    E redondeada (O/ER)     F fruncida (U/W)
    G dientes sobre labio (F/V)                    H lengua arriba (L)
    X reposo
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

# Logo en alta que paso Javier (1254x1254): la cabeza sale a 540 px contra los
# 275 del logo del repo, o sea el doble de detalle justo en el hocico, que es
# donde se dibuja.
LOGO = Path("analisis/mascota_gato/entrada/logo_hd.jpg")

NARIZ = (626, 536)     # centro de la nariz, en coordenadas del logo
ANCHO_CABEZA = 540     # ancho de la cabeza en el logo; escala el tamano de la boca
SEPARACION_BOCA = 56   # cuanto baja la boca respecto de la nariz, en px del logo

# x, y, ancho, alto del recorte + escala a la que se dibuja.
ENCUADRES = {
    # Corta en y=620: mas abajo entran astillas de la pata y del cuello.
    "cabeza": {"recorte": (360, 130, 540, 490), "escala": 2.0, "relleno_abajo": 130},
    "busto": {"recorte": (250, 130, 750, 660), "escala": 1.45, "relleno_abajo": 60},
    # `boca` agranda las formas respecto de la cabeza. En emblema el gato se ve
    # entero pero mas chico, asi que a tamano "natural" la articulacion no se
    # lee en pantalla: se exagera, como en cualquier caricatura.
    "emblema": {"recorte": (232, 118, 782, 782), "escala": 1.40, "relleno_abajo": 0,
                "boca": 1.75},
}

# Paleta tomada del propio logo.
CONTORNO = (26, 20, 18)
INTERIOR = (52, 30, 28)
LENGUA = (176, 96, 96)
DIENTES = (248, 243, 232)
ORO = (214, 176, 106)

FORMAS = ("A", "B", "C", "D", "E", "F", "G", "H", "X")


def _silueta(logo: np.ndarray) -> np.ndarray:
    """Alfa del gato: 255 donde esta el personaje, 0 en el fondo del logo."""
    h, w = logo.shape[:2]
    b, g, r = (logo[:, :, i].astype(np.int16) for i in range(3))
    navy = ((b - r) > 12) & (b < 90)
    blanco = (b > 230) & (g > 230) & (r > 230)

    # Fondo = solo las manchas de azul/blanco que TOCAN el borde de la imagen.
    # Con un umbral de color a secas se perdian los contornos del dibujo, que
    # son del mismo azul marino que el fondo.
    n, etiquetas = cv2.connectedComponents((navy | blanco).astype(np.uint8))
    del n
    del g
    bordes = set(etiquetas[0]) | set(etiquetas[-1]) | set(etiquetas[:, 0]) | set(etiquetas[:, -1])
    bordes.discard(0)
    fondo = np.isin(etiquetas, list(bordes))

    n2, et2 = cv2.connectedComponents((~fondo).astype(np.uint8))
    del n2
    gato = (et2 == et2[int(h * 0.35), w // 2]).astype(np.uint8)

    gato = _rellenar_huecos(gato)
    # Cierra las muescas que dejan las rayas oscuras del pelaje donde tocan el
    # borde de la silueta: sin esto los hombros quedan comidos a mordiscos.
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    gato = _rellenar_huecos(cv2.morphologyEx(gato, cv2.MORPH_CLOSE, nucleo))
    return (gato * 255).astype(np.uint8)


def _rellenar_huecos(mascara: np.ndarray) -> np.ndarray:
    """Rellena los agujeros interiores (corbata, ojos, interior de los lentes)."""
    h, w = mascara.shape
    fuera = mascara.copy()
    cv2.floodFill(fuera, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    return (mascara | (1 - fuera)).astype(np.uint8)


def _base(modo: str) -> tuple[Image.Image, float]:
    """Sprite base (sin boca) y el factor de escala del dibujo."""
    logo = cv2.imread(str(LOGO))
    if logo is None:
        raise SystemExit(f"No pude leer el logo en {LOGO}")

    cfg = ENCUADRES[modo]
    x, y, w, h = cfg["recorte"]
    escala = cfg["escala"]
    recorte = logo[y:y + h, x:x + w]

    if modo == "emblema":
        # El fondo azul del logo se queda: es parte de la insignia. Solo se
        # recorta en circulo y se le pone el aro dorado de la marca.
        alfa = np.zeros((h, w), np.uint8)
        cv2.ellipse(alfa, (w // 2, h // 2), (w // 2 - 2, h // 2 - 2), 0, 0, 360, 255, -1)
    else:
        alfa = _silueta(logo)[y:y + h, x:x + w]

    rgba = np.dstack([cv2.cvtColor(recorte, cv2.COLOR_BGR2RGB), alfa])
    img = Image.fromarray(rgba, "RGBA").resize(
        (round(w * escala), round(h * escala)), Image.LANCZOS
    )

    if modo == "emblema":
        d = ImageDraw.Draw(img)
        margen = round(6 * escala)
        d.ellipse([margen, margen, img.width - margen - 1, img.height - margen - 1],
                  outline=ORO, width=max(3, round(5 * escala)))

    relleno = round(cfg["relleno_abajo"] * escala)
    if relleno:
        lienzo = Image.new("RGBA", (img.width, img.height + relleno), (0, 0, 0, 0))
        lienzo.paste(img, (0, 0))
        img = lienzo

    # La boca se dibuja siempre del mismo tamano RELATIVO a la cabeza, no al
    # lienzo: en busto y emblema la cabeza ocupa menos y las formas tienen que
    # encoger con ella.
    return img, ANCHO_CABEZA * escala / 1080.0 * cfg.get("boca", 1.0)


def _ancla(modo: str) -> tuple[int, int]:
    x, y, _, _ = ENCUADRES[modo]["recorte"]
    escala = ENCUADRES[modo]["escala"]
    nx, ny = NARIZ
    return (round((nx - x) * escala), round((ny - y + SEPARACION_BOCA) * escala))


def _boca(draw: ImageDraw.ImageDraw, forma: str, cx: int, cy: int, k: float) -> None:
    """Dibuja una forma de boca centrada en (cx, cy), a escala k."""
    borde = max(2, round(2 * k))

    def p(v):
        return round(v * k)

    def elipse(ancho, alto):
        caja = [cx - p(ancho) // 2, cy - p(alto) // 2, cx + p(ancho) // 2, cy + p(alto) // 2]
        draw.ellipse(caja, fill=INTERIOR, outline=CONTORNO, width=borde)
        return caja

    if forma in ("A", "X"):
        # Boca cerrada: la curva tipica de gato. X es el reposo, A el cierre de
        # P/B/M; cambia el ancho para que la transicion se note aunque las dos
        # esten cerradas.
        ancho = p(62 if forma == "A" else 52)
        draw.arc([cx - ancho, cy - p(46), cx + ancho, cy + p(6)], 20, 160,
                 fill=CONTORNO, width=borde + 1)
    elif forma == "B":
        caja = elipse(116, 36)
        draw.line([caja[0] + borde, cy, caja[2] - borde, cy], fill=DIENTES, width=borde)
    elif forma == "C":
        elipse(114, 70)
    elif forma == "D":
        caja = elipse(122, 114)
        draw.ellipse([cx - p(38), caja[3] - p(52), cx + p(38), caja[3] - p(8)],
                     fill=LENGUA, outline=None)
    elif forma == "E":
        elipse(90, 64)
    elif forma == "F":
        elipse(58, 58)
    elif forma == "G":
        caja = elipse(100, 44)
        draw.line([caja[0] + borde, cy - p(8), caja[2] - borde, cy - p(8)],
                  fill=DIENTES, width=borde + 2)
    elif forma == "H":
        elipse(100, 76)
        draw.ellipse([cx - p(28), cy - p(24), cx + p(28), cy + p(14)],
                     fill=LENGUA, outline=None)
    else:
        raise ValueError(f"Forma desconocida: {forma}")


def generar(destino: Path, modo: str) -> list[Path]:
    base, k = _base(modo)
    cx, cy = _ancla(modo)
    destino.mkdir(parents=True, exist_ok=True)
    escritos = []
    for forma in FORMAS:
        img = base.copy()
        _boca(ImageDraw.Draw(img), forma, cx, cy, k)
        ruta = destino / f"{forma}.png"
        img.save(ruta)
        escritos.append(ruta)
    return escritos


def exportar_para_pipeline(destino: Path, modo: str) -> Path:
    """Escribe la carpeta de mascota con el layout que espera el narrador.

        <destino>/idle/00.png        boca en reposo
        <destino>/talk/00.png,01.png boca abierta / media
        <destino>/visemas/A..X.png   las 9 formas de Rhubarb

    `idle` y `talk` existen porque el compositor las exige y son su plan B: si
    por lo que sea no hay visemas, la mascota sigue moviendo la boca por
    amplitud en vez de quedarse congelada.
    """
    destino.mkdir(parents=True, exist_ok=True)
    visemas = destino / "visemas"
    generar(visemas, modo)

    from shutil import copyfile

    for accion, formas in (("idle", ["X"]), ("talk", ["C", "A"])):
        carpeta = destino / accion
        carpeta.mkdir(parents=True, exist_ok=True)
        for i, forma in enumerate(formas):
            copyfile(visemas / f"{forma}.png", carpeta / f"{i:02d}.png")
    return destino


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--modo", default="cabeza", choices=sorted(ENCUADRES))
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pipeline", action="store_true",
                    help="escribe idle/, talk/ y visemas/ para el narrador")
    ap.add_argument("--logo", type=Path, help="imagen de origen (def. el logo del canal)")
    ap.add_argument("--recorte", help="x,y,w,h del emblema dentro de la imagen")
    ap.add_argument("--nariz", help="x,y de la nariz, en coordenadas de la imagen")
    ap.add_argument("--escala", type=float, help="factor de escalado del recorte")
    ap.add_argument("--ancho-cabeza", type=int,
                    help="ancho de la cabeza en la imagen; fija el tamano de la boca")
    ap.add_argument("--boca", type=float,
                    help="exagera la boca respecto de la cabeza (def. 1.75 en emblema)")
    args = ap.parse_args()

    # Override de la configuracion del modulo: un emblema de tema tiene otro
    # tamano y otra posicion de nariz que el logo original.
    global LOGO, NARIZ, ANCHO_CABEZA
    if args.logo:
        LOGO = args.logo
    if args.nariz:
        NARIZ = tuple(int(v) for v in args.nariz.split(","))
    if args.ancho_cabeza:
        ANCHO_CABEZA = args.ancho_cabeza
    cfg = ENCUADRES[args.modo]
    if args.recorte:
        cfg["recorte"] = tuple(int(v) for v in args.recorte.split(","))
    if args.escala:
        cfg["escala"] = args.escala
    if args.boca:
        cfg["boca"] = args.boca

    if args.pipeline:
        exportar_para_pipeline(args.out, args.modo)
        tam = Image.open(args.out / "visemas" / "X.png").size
        print(f"mascota {args.modo} {tam[0]}x{tam[1]} en {args.out}")
        print("  idle/  talk/  visemas/")
        return 0

    escritos = generar(args.out, args.modo)
    tam = Image.open(escritos[0]).size
    print(f"{len(escritos)} sprites {tam[0]}x{tam[1]} ({args.modo}) en {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
