"""Re-ensambla un video ya generado subiendo los subtitulos -- SUELTO, fuera del pipeline.

El avatar va en la esquina de abajo y los subtitulos, con el margen historico
(14% del alto), le pasan por encima. Esto vuelve a ensamblar el video a partir
de los clips YA renderizados, cambiando UNICAMENTE el MarginV del estilo
Caption en el .ass.

No re-alinea, no re-genera imagenes ni medios: reusa clips/, narracion.wav y la
cama de audio tal cual estan. Asi las duraciones no cambian ni un frame y el
avatar generado contra el audio del video viejo sigue en sincronia.

    python tools/reensamblar_subs_arriba.py --proyecto guion-debanhi-escobar \
        --margen-rel 0.28 --out analisis/poc_avatar/final_subs_arriba.mp4
"""

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path

NARRATOR = Path("C:/illustrated-narrator")
sys.path.insert(0, str(NARRATOR / "src"))


def _log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def _subir_captions(origen: Path, destino: Path, margen_rel: float) -> int:
    """Copia el .ass cambiando solo el MarginV del estilo Caption.

    El alto sale del PlayResY del propio .ass, no del canvas del contenedor:
    ese canvas depende de NARR_VERTICAL y fuera del pipeline vale 1920x1080
    aunque los clips sean 1080x1920 -- con el alto equivocado el margen se
    calcula sobre 1080 y los subtitulos suben la mitad de lo pedido.
    """
    lineas = origen.read_text(encoding="utf-8").splitlines()
    alto = next(
        (int(l.split(":", 1)[1]) for l in lineas if l.startswith("PlayResY:")), 0
    )
    if alto <= 0:
        raise SystemExit(f"No pude leer PlayResY de {origen}")
    nuevo = int(alto * margen_rel)
    tocadas = 0
    for i, linea in enumerate(lineas):
        if not linea.startswith("Style: Caption,"):
            continue
        # MarginV es el penultimo campo del formato Style (antes de Encoding).
        campos = linea.split(",")
        campos[-2] = str(nuevo)
        lineas[i] = ",".join(campos)
        tocadas += 1
    if tocadas != 1:
        raise SystemExit(f"Esperaba 1 estilo Caption en {origen}, encontre {tocadas}")
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return nuevo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--proyecto", required=True)
    ap.add_argument("--margen-rel", type=float, default=0.28)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    from illustrated_narrator.infrastructure.config import load_settings
    from illustrated_narrator.infrastructure.container import Container

    ajustes = load_settings()
    proyecto = ajustes.projects_dir / args.proyecto
    if not proyecto.exists():
        raise SystemExit(f"No existe el proyecto {proyecto}")

    # Orden alfabetico = orden del timeline: aaa_intro, p00..pNN, zzz_end_card.
    # Es el mismo criterio con el que el pipeline los nombro.
    clips = sorted((proyecto / "clips").glob("*.mp4"))
    if not clips:
        raise SystemExit(f"No hay clips en {proyecto / 'clips'}")

    contenedor = Container(ajustes)

    ass_alto = args.out.parent / f"{args.out.stem}.ass"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    margen_px = _subir_captions(proyecto / "captions.ass", ass_alto, args.margen_rel)

    cama = proyecto / "assets" / "auto" / "bed.wav"
    _log(f"clips   : {len(clips)} ({clips[0].name} .. {clips[-1].name})")
    _log(f"MarginV : {margen_px}px desde abajo ({args.margen_rel:.0%} del alto)")
    _log(f"cama    : {'si' if cama.exists() else 'no'}")

    inicio = time.time()
    contenedor.video_assembler.assemble(
        clips,
        ass_alto,
        proyecto / "narracion.wav",
        args.out,
        # El default de assemble() es 0.5, pero el pipeline usa el de settings
        # (0.28). Con otro valor cambian las duraciones y el avatar se desfasa.
        xfade_duration=ajustes.xfade_duration,
        bed_path=cama if cama.exists() else None,
        # Sin tarjeta de marca en este formato: la narracion arranca en t=0.
        audio_delay_seconds=0.0,
    )
    _log(f"LISTO en {time.time() - inicio:.0f}s -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
