"""Genera un video de punta a punta SIN subirlo a Drive ni tocar el calendario.

    python tools/poc_formato_nuevo.py <slug>

Reusa los mismos pasos que `pipeline.run`, pero se saltea la subida y la
asignación de fecha de publicación: es para validar cambios de formato, no
para producir un video del canal.
"""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BOT = Path(r"C:\dato-mata-gato-bot")
load_dotenv(BOT / ".env")
sys.path.insert(0, str(BOT / "src"))

from dato_mata_gato_bot import avatar_presentador, pipeline, sessions  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    slug = sys.argv[1]

    falta = pipeline.motor_tts_listo()
    if falta:
        _log(f"FALLÓ: {falta}")
        return 1
    falta = avatar_presentador.disponible()
    if falta:
        _log(f"FALLÓ: {falta}")
        return 1

    inicio = time.time()
    _log(f"1/4 generando audio con {pipeline.motor_tts()}")
    pipeline._stage_guion_for_tts(slug)
    ok, salida = pipeline._generate_audio(slug, sessions.DEFAULT_VOICE)
    if not ok:
        _log(f"FALLÓ la síntesis:\n{salida[-2000:]}")
        return 1

    _log("2/4 armando el proyecto del narrador")
    pipeline._setup_narrator_project(slug)
    # La alineación vieja no sirve: el audio nuevo no dura lo mismo y el
    # narrador la daría por buena, montando el video con los tiempos
    # anteriores sobre la voz nueva, sin error alguno.
    proyecto = pipeline.NARRATOR_PROJECTS / slug
    for nombre in ("transcript.json", "planos_alineados.json", "visemas.json"):
        (proyecto / nombre).unlink(missing_ok=True)

    _log("3/4 corriendo narrator generate (modo avatar)")
    ok, salida = pipeline._run_narrator_generate(slug, avatar=True)
    if not ok:
        _log(f"FALLÓ el narrador:\n{salida[-2500:]}")
        return 1

    final = proyecto / "final.mp4"
    if not final.exists():
        _log("el narrador terminó pero no hay final.mp4")
        return 1
    _log(f"   video base: {final} ({final.stat().st_size / 1e6:.1f} MB)")

    _log("4/4 agregando el presentador (~35 min)")
    avatar_presentador.componer(final, progreso=lambda p: _log(f"   {p}"))

    _log(f"LISTO en {(time.time() - inicio) / 60:.1f} min -> {final}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
