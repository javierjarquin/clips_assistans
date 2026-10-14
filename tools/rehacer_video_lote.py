"""Regenera UN video y lo archiva en la carpeta de un lote, sin publicarlo.

    python tools/rehacer_video_lote.py <slug> <carpeta-del-lote>

Para completar un lote al que le faltó un video: reusa exactamente el mismo
camino que `/generargrande` (mismo pipeline, mismo archivado, sin Drive), así
que el resultado es indistinguible de los que salieron en la corrida.
"""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BOT = Path(r"C:\dato-mata-gato-bot")
load_dotenv(BOT / ".env")
sys.path.insert(0, str(BOT / "src"))

from dato_mata_gato_bot import pipeline, sessions  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    slug, carpeta = sys.argv[1], Path(sys.argv[2])
    inicio = time.time()

    def paso(p: str) -> None:
        print(f"[{time.strftime('%H:%M:%S')}] {p}", flush=True)

    falta = pipeline.motor_tts_listo()
    if falta:
        print(f"FALLÓ: {falta}")
        return 1

    res = pipeline.run(slug, sessions.DEFAULT_VOICE, None, False, None, carpeta)
    paso(f"{'LISTO' if res.ok else 'FALLÓ'} en {(time.time()-inicio)/60:.1f} min")
    print(res.mensaje[:1500])
    return 0 if res.ok else 1


if __name__ == "__main__":
    sys.exit(main())
