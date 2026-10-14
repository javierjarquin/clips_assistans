"""Anima al gato de Dato Mata Gato con los visemas de Rhubarb -- SUELTO.

Toma la salida JSON de Rhubarb Lip Sync (`mouthCues`) y los sprites de
`gato_sprites.py`, y escribe dos videos: el gato en RGB y su mascara alfa. Los
consume `poc_avatar_overlay.py --mascara`, igual que el avatar de MuseTalk, asi
las dos versiones se componen exactamente con el mismo codigo y se pueden
comparar de verdad.

    python tools/gato_animar.py --visemas visemas.json --sprites sprites/ \
        --duracion 120.1 --out gato.mp4 --mascara gato_mascara.mkv

Ademas de la boca hay un balanceo suave (respiracion + inclinacion): sin eso el
personaje parece una calcomania pegada, aunque la boca se mueva bien.
"""

import argparse
import json
import math
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image

FPS = 25
ANCHO_TRABAJO = 550   # se escala a ~270 en la composicion final
REPOSO = "X"


def _log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def _formas_por_fotograma(cues: list[dict], n: int) -> list[str]:
    """Forma de boca para cada fotograma, muestreando la linea de tiempo."""
    formas = [REPOSO] * n
    for cue in cues:
        ini = int(round(cue["start"] * FPS))
        fin = int(round(cue["end"] * FPS))
        # Al menos un fotograma: Rhubarb emite tramos mas cortos que 1/25s y si
        # se redondean a cero la silaba desaparece de la animacion.
        fin = max(fin, ini + 1)
        for i in range(max(0, ini), min(n, fin)):
            formas[i] = cue["value"]
    return formas


def _cargar_sprites(carpeta: Path, ancho: int) -> dict[str, Image.Image]:
    sprites = {}
    for ruta in sorted(carpeta.glob("*.png")):
        img = Image.open(ruta).convert("RGBA")
        alto = round(img.height * ancho / img.width)
        sprites[ruta.stem] = img.resize((ancho, alto), Image.LANCZOS)
    if REPOSO not in sprites:
        raise SystemExit(f"Falta {REPOSO}.png en {carpeta}")
    return sprites


def _tuberia(destino: Path, ancho: int, alto: int, pix_fmt: str, args_cod: list[str]):
    destino.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", pix_fmt, "-s", f"{ancho}x{alto}",
         "-r", str(FPS), "-i", "-", *args_cod, str(destino)],
        stdin=subprocess.PIPE,
    )


def animar(visemas: Path, sprites_dir: Path, duracion: float,
           destino: Path, mascara: Path, balanceo: bool = True) -> float:
    datos = json.loads(visemas.read_text(encoding="utf-8"))
    cues = datos.get("mouthCues") or []
    if not cues:
        raise SystemExit(f"{visemas} no tiene mouthCues")

    total = int(round(duracion * FPS))
    formas = _formas_por_fotograma(cues, total)
    sprites = _cargar_sprites(sprites_dir, ANCHO_TRABAJO)
    alto_sprite = sprites[REPOSO].height

    # Margen para que la inclinacion no recorte las orejas.
    margen = 26
    # Pares obligatorios: libx264 con yuv420p no abre el codificador con un
    # lado impar, y falla con un "Could not open encoder before EOF" que no
    # menciona las dimensiones.
    W = (ANCHO_TRABAJO + margen * 2) // 2 * 2
    H = (alto_sprite + margen * 2) // 2 * 2
    _log(f"lienzo : {W}x{H}, {total} fotogramas ({duracion:.1f}s)")
    _log(f"formas : {sorted(set(formas))}")

    rgb = _tuberia(destino, W, H, "rgb24",
                   ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p"])
    # La mascara va sin perdida: comprimida deja un halo de bloque en el borde.
    alfa = _tuberia(mascara, W, H, "gray", ["-c:v", "ffv1", "-pix_fmt", "gray"])

    inicio = time.time()
    try:
        for i, forma in enumerate(formas):
            sprite = sprites.get(forma, sprites[REPOSO])
            lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if balanceo:
                t = i / FPS
                # Respiracion (0.45 Hz) + un vaiven mas lento; amplitudes chicas
                # a proposito, la idea es que se note vivo, no que cabecee.
                dy = round(3.5 * math.sin(2 * math.pi * 0.45 * t))
                dx = round(2.5 * math.sin(2 * math.pi * 0.17 * t))
                giro = 1.1 * math.sin(2 * math.pi * 0.11 * t)
                sprite = sprite.rotate(giro, resample=Image.BICUBIC, expand=False)
            else:
                dx = dy = 0
            lienzo.paste(sprite, (margen + dx, margen + dy), sprite)
            arr = np.asarray(lienzo)
            rgb.stdin.write(np.ascontiguousarray(arr[:, :, :3]).tobytes())
            alfa.stdin.write(np.ascontiguousarray(arr[:, :, 3]).tobytes())
            if i and i % 500 == 0:
                _log(f"  {i}/{total}")
    finally:
        for p in (rgb, alfa):
            if p.stdin:
                p.stdin.close()
            p.wait()

    for p, nombre in ((rgb, "video"), (alfa, "mascara")):
        if p.returncode != 0:
            raise SystemExit(f"ffmpeg fallo escribiendo la {nombre} (codigo {p.returncode})")
    return time.time() - inicio


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--visemas", required=True, type=Path)
    ap.add_argument("--sprites", required=True, type=Path)
    ap.add_argument("--duracion", required=True, type=float, help="segundos del video final")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--mascara", required=True, type=Path)
    ap.add_argument("--sin-balanceo", action="store_true")
    args = ap.parse_args()

    t = animar(args.visemas, args.sprites, args.duracion, args.out, args.mascara,
               not args.sin_balanceo)
    _log(f"LISTO en {t:.0f}s -> {args.out} + {args.mascara}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
