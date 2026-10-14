"""Genera un clip de video con IA y mide cuánto tarde, para decidir si vale.

    python tools/prueba_video_ia.py [segundos] [ancho] [alto]

Existe para contestar una pregunta concreta: ¿conviene bajar la cantidad de
videos por día a cambio de generar cada toma con IA en vez de buscar stock?
La respuesta depende del tiempo por segundo de video en ESTA máquina, y eso
solo se sabe midiéndolo.
"""

import sys
import time
from pathlib import Path

NARRADOR = Path(r"C:\illustrated-narrator")
sys.path.insert(0, str(NARRADOR / "src"))

from illustrated_narrator.adapters.video.animatediff_a1111_adapter import (  # noqa: E402
    AnimateDiffA1111Adapter,
)
from illustrated_narrator.ports.video_generator import VideoGenerationRequest  # noqa: E402

# Prompt típico del canal: atmósfera, sin personas identificables.
PROMPT = ("cinematic night street in a mexican border town, empty, police tape "
          "in the foreground, documentary photography, moody, 2005, no people")
NEGATIVO = "people, faces, text, watermark, logo, cartoon, distorted"


def main() -> int:
    segundos = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    ancho = int(sys.argv[2]) if len(sys.argv) > 2 else 512
    alto = int(sys.argv[3]) if len(sys.argv) > 3 else 512

    adaptador = AnimateDiffA1111Adapter("http://127.0.0.1:7860")
    if not adaptador.is_available():
        print("A1111 no responde. Levantalo antes (tools/run_a1111.bat).")
        return 1

    destino = Path(r"C:\clip_assistance\analisis\ia_test") / f"clip_{ancho}x{alto}_{segundos:g}s.mp4"
    destino.parent.mkdir(parents=True, exist_ok=True)
    pedido = VideoGenerationRequest(
        prompt=PROMPT, negative_prompt=NEGATIVO,
        width=ancho, height=alto, duration_seconds=segundos, fps=8,
    )
    fotogramas = max(8, round(segundos * 8))
    print(f"generando {fotogramas} fotogramas ({segundos:g}s a 8 fps) en {ancho}x{alto}...", flush=True)

    inicio = time.time()
    try:
        salida = adaptador.generate(pedido, destino)
    except Exception as exc:  # noqa: BLE001 -- el punto de la prueba es ver si falla
        print(f"FALLÓ tras {(time.time()-inicio)/60:.1f} min: {type(exc).__name__}: {exc}")
        return 1
    tardo = time.time() - inicio

    print(f"\nLISTO en {tardo/60:.1f} min  ->  {salida}")
    print(f"  {tardo/segundos:.0f} segundos de máquina por segundo de video")
    print(f"  un video de 70s costaría {tardo/segundos*70/3600:.1f} horas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
