"""Superpone el avatar sobre un video ya terminado -- SUELTO, fuera del pipeline.

Toma el final.mp4 tal como lo produce el pipeline hoy y le pega el clip del
avatar en una esquina, con máscara ovalada para que no se vea el recuadro con
la habitación de fondo.

    python tools/poc_avatar_overlay.py --video final.mp4 --avatar avatar.mp4 \\
        --out final_con_avatar.mp4

Se hace como POST-PROCESO a propósito: el pipeline no se entera. Si el avatar
falla o tarda de más, el video sale igual que siempre.
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Fracción del ANCHO del video que ocupa el avatar. El usuario pidió "a lo
# mucho una cuarta parte de la pantalla".
ANCHO_REL_DEFAULT = 0.25
MARGEN_REL = 0.03  # separación del borde, como fracción del ancho

POSICIONES = ("abajo-derecha", "abajo-izquierda", "arriba-derecha", "arriba-izquierda")


class OverlayError(RuntimeError):
    pass


def _log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def _dimensiones(video: Path) -> tuple[int, int]:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(video)],
        capture_output=True, text=True, timeout=60,
    ).stdout.strip()
    try:
        w, h = salida.split("x")[:2]
        return int(w), int(h)
    except ValueError as exc:
        raise OverlayError(f"No pude leer las dimensiones de {video}: {salida!r}") from exc


def _posicion(pos: str, W: int, H: int, aw: int, ah: int) -> tuple[str, str]:
    margen = int(W * MARGEN_REL)
    x_der, x_izq = W - aw - margen, margen
    y_abajo, y_arriba = H - ah - margen, margen
    return {
        "abajo-derecha": (str(x_der), str(y_abajo)),
        "abajo-izquierda": (str(x_izq), str(y_abajo)),
        "arriba-derecha": (str(x_der), str(y_arriba)),
        "arriba-izquierda": (str(x_izq), str(y_arriba)),
    }[pos]


def componer(
    video: Path,
    avatar: Path,
    destino: Path,
    ancho_rel: float = ANCHO_REL_DEFAULT,
    posicion: str = "abajo-derecha",
    ovalo: bool = True,
    recorte: str | None = None,
    mascara_path: Path | None = None,
    fundido_abajo: float = 0.12,
) -> float:
    for ruta, nombre in ((video, "video"), (avatar, "avatar")):
        if not ruta.exists():
            raise OverlayError(f"No existe el {nombre}: {ruta}")
    if posicion not in POSICIONES:
        raise OverlayError(f"Posición inválida: {posicion}. Opciones: {', '.join(POSICIONES)}")

    W, H = _dimensiones(video)
    aw = int(W * ancho_rel) // 2 * 2  # par: libx264 rechaza dimensiones impares
    av_w, av_h = _dimensiones(avatar)
    if recorte:
        # La placa es 9:16 completa: a 1/4 de pantalla la cara queda diminuta y
        # entra media habitacion. Recortando alrededor de la cara antes de
        # escalar, el avatar se lee aunque sea chico.
        try:
            cw, ch, cx, cy = (int(v) for v in recorte.split(":"))
        except ValueError as exc:
            raise OverlayError(f"--recorte debe ser w:h:x:y, recibí {recorte!r}") from exc
        if cx + cw > av_w or cy + ch > av_h:
            raise OverlayError(
                f"El recorte {recorte} se sale del avatar ({av_w}x{av_h})"
            )
        av_w, av_h = cw, ch
    ah = int(aw * av_h / av_w) // 2 * 2
    x, y = _posicion(posicion, W, H, aw, ah)

    _log(f"video  : {W}x{H}")
    _log(f"avatar : {aw}x{ah} en {posicion} (x={x}, y={y})")

    pre = f"crop={recorte}," if recorte else ""

    if mascara_path is not None:
        # Recorte real de la persona: la mascara viene de poc_avatar_recorte.py
        # y se recorta y escala IGUAL que el avatar, si no queda corrida.
        # El fundido de abajo va aca (no en la mascara) porque depende del
        # encuadre: sin el, la silueta termina en un corte recto en el pecho.
        filas = max(1, int(ah * fundido_abajo))
        desvanecer = (
            f",geq=lum='lum(X,Y)*min(1,({ah}-Y)/{filas})'" if fundido_abajo > 0 else ""
        )
        cadena = (
            f"[1:v]{pre}scale={aw}:{ah},format=rgba[av];"
            f"[2:v]{pre}scale={aw}:{ah},format=gray{desvanecer}[am];"
            f"[av][am]alphamerge[avm];[0:v][avm]overlay={x}:{y}[v]"
        )
    elif ovalo:
        # Máscara ovalada con geq sobre el canal alfa: recorta la habitación de
        # fondo sin necesidad de un modelo de segmentación. El borde se suaviza
        # con un degradado de ~6% del radio para que no quede aserrado.
        mascara = (
            "format=rgba,"
            "geq="
            "r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
            f"a='255*clip((1-((pow((X-{aw}/2)/({aw}/2),2)+pow((Y-{ah}/2)/({ah}/2),2)))) / 0.12, 0, 1)'"
        )
        cadena = f"[1:v]{pre}scale={aw}:{ah},{mascara}[av];[0:v][av]overlay={x}:{y}[v]"
    else:
        cadena = f"[1:v]{pre}scale={aw}:{ah}[av];[0:v][av]overlay={x}:{y}[v]"

    destino.parent.mkdir(parents=True, exist_ok=True)
    entradas = ["-i", str(video), "-i", str(avatar)]
    if mascara_path is not None:
        if not mascara_path.exists():
            raise OverlayError(f"No existe la mascara: {mascara_path}")
        entradas += ["-i", str(mascara_path)]

    args = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        *entradas,
        "-filter_complex", cadena,
        "-map", "[v]",
        # El audio sale del video original: el del avatar es el mismo, y usar
        # el original evita cualquier desfase introducido por MuseTalk.
        "-map", "0:a?",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(destino),
    ]

    inicio = time.time()
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    transcurrido = time.time() - inicio
    if proc.returncode != 0:
        raise OverlayError(f"ffmpeg falló:\n{(proc.stderr or '')[-1500:]}")
    if not destino.exists():
        raise OverlayError(f"ffmpeg terminó sin error pero no dejó {destino}")
    return transcurrido


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True, type=Path, help="final.mp4 del pipeline")
    ap.add_argument("--avatar", required=True, type=Path, help="clip del avatar")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--ancho", type=float, default=ANCHO_REL_DEFAULT,
                    help=f"ancho del avatar como fracción del video (def. {ANCHO_REL_DEFAULT})")
    ap.add_argument("--pos", default="abajo-derecha", choices=POSICIONES)
    ap.add_argument("--sin-ovalo", action="store_true", help="deja el recuadro rectangular")
    ap.add_argument("--recorte", help="recorte del avatar antes de escalar, en w:h:x:y")
    ap.add_argument("--mascara", type=Path,
                    help="mascara de poc_avatar_recorte.py: recorta la persona en vez del ovalo")
    ap.add_argument("--fundido-abajo", type=float, default=0.12,
                    help="fraccion del alto que se funde a transparente abajo (def. 0.12)")
    args = ap.parse_args()

    try:
        t = componer(args.video, args.avatar, args.out, args.ancho, args.pos,
                     not args.sin_ovalo, args.recorte, args.mascara, args.fundido_abajo)
    except OverlayError as exc:
        _log("FALLÓ")
        print(f"\n{exc}", file=sys.stderr)
        return 1

    _log(f"LISTO en {t:.0f}s -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
