"""POC de voz: un video ya hecho, rearmado con otra voz de VoiceStudio.

Trabaja sobre una COPIA del guion (slug <origen>-<sufijo>): mismo guion y
mismas imágenes, solo cambia la voz, así el original queda para comparar.
Rehace audio, alineación y ensamblado como tools/regenerar_voz.py del bot, con
el gato en la esquina como en producción.

Al final avisa por Telegram con una versión liviana (el bot no acepta más de
50 MB y un final pesa ~130).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\poc_voz.py \\
        --origen guion-tierra-blanca-veracruz --voz 746b6e2d --sufijo fish2 --num-step 32
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BOT = Path(r"C:\dato-mata-gato-bot")
sys.path.insert(0, str(BOT / "src"))

ap = argparse.ArgumentParser()
ap.add_argument("--origen", required=True, help="slug del video ya hecho")
ap.add_argument("--voz", required=True, help="profile_id de VoiceStudio")
ap.add_argument("--sufijo", required=True, help="para el slug de la copia")
ap.add_argument("--num-step", type=int, help="pasos de VoiceStudio (32 = calidad)")
ap.add_argument("--etiqueta", help="nombre de la voz en los avisos")
ap.add_argument("--retomar", action="store_true",
                help="sigue una corrida cortada: no recopia ni borra los planos ya sintetizados")
ARGS = ap.parse_args()

# ANTES de cargar el .env: load_dotenv no pisa lo que ya está en el entorno,
# así la voz de producción queda intacta en el .env.
os.environ["VOICESTUDIO_VOICE_ID"] = ARGS.voz
os.environ["TTS_ENGINE"] = "voicestudio"
if ARGS.num_step:
    os.environ["VOICESTUDIO_NUM_STEP"] = str(ARGS.num_step)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BOT / ".env")

import requests  # noqa: E402

from dato_mata_gato_bot import pipeline  # noqa: E402

ORIGEN = ARGS.origen
SLUG = f"{ORIGEN}-{ARGS.sufijo}"
NOMBRE = ARGS.etiqueta or ARGS.sufijo
SALIDA = Path(r"C:\Android_in\lotes") / f"poc-voz-{ARGS.sufijo}"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")[0].strip()


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def telegram(texto: str, video: Path | None = None) -> None:
    if not (TOKEN and CHAT_ID):
        return
    try:
        if video is None:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          data={"chat_id": CHAT_ID, "text": texto}, timeout=30)
        else:
            with open(video, "rb") as f:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                              data={"chat_id": CHAT_ID, "caption": texto,
                                    "supports_streaming": "true"},
                              files={"video": f}, timeout=600)
    except Exception as exc:  # noqa: BLE001 -- el aviso no tira el POC
        log(f"no se pudo avisar por Telegram: {exc}")


def copiar(origen: Path, destino: Path, sin: tuple[str, ...] = ()) -> None:
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(origen, destino, ignore=shutil.ignore_patterns(*sin))


def duracion(ruta: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(ruta)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def main() -> int:
    if ARGS.retomar and (pipeline.ANDROID_IN / SLUG).exists():
        # Misma voz que la corrida cortada: la caché de tts-kokoro salta los
        # planos que ya están (con B, cada plano cuesta varios minutos).
        log(f"retomando {SLUG}")
    else:
        log(f"copiando {ORIGEN} -> {SLUG}")
        copiar(pipeline.ANDROID_IN / ORIGEN, pipeline.ANDROID_IN / SLUG)
        # Imágenes y medios se reusan; lo que depende de la voz vieja NO se copia.
        copiar(pipeline.NARRATOR_PROJECTS / ORIGEN, pipeline.NARRATOR_PROJECTS / SLUG,
               sin=("final.mp4", "narracion.wav", "transcript.json", "planos_alineados.json",
                    "visemas.json", "captions.ass", "clips", "_silencios",
                    "hoja_de_contacto.jpg"))
        # Sin esto tts-kokoro reusaría los WAV de otra voz si la copia existía.
        shutil.rmtree(pipeline.TTS_KOKORO_PROJECTS / SLUG, ignore_errors=True)
        pipeline._stage_guion_for_tts(SLUG)

    falta = pipeline.motor_tts_listo()
    if falta:
        telegram(f"POC voz {NOMBRE}: no arrancó. {falta}")
        log(falta)
        return 1

    telegram(f"POC voz {NOMBRE}: arranqué con {ORIGEN} (mismo guion e imágenes, "
             "solo cambia la voz). Te aviso cuando esté.")
    inicio = time.time()
    log(f"sintetizando con el perfil {ARGS.voz} (num_step={ARGS.num_step or 'default'})")
    ok, out = pipeline._generate_audio(SLUG, "am_adam")
    if not ok:
        telegram(f"POC voz {NOMBRE}: falló la voz.\n{out[-600:]}")
        log(out)
        return 1
    log(f"voz lista en {(time.time() - inicio) / 60:.0f} min")

    pipeline._setup_narrator_project(SLUG)
    pipeline._kick_off_a1111_if_needed()
    pipeline._esperar_a1111()
    log("narrator generate")
    ok, out = pipeline._run_narrator_generate(SLUG)
    final = pipeline.NARRATOR_PROJECTS / SLUG / "final.mp4"
    if not ok or not final.exists():
        telegram(f"POC voz {NOMBRE}: falló el armado del video.\n{out[-600:]}")
        log(out)
        return 1

    SALIDA.mkdir(parents=True, exist_ok=True)
    completo = SALIDA / f"{SLUG}.mp4"
    shutil.copy2(final, completo)
    liviano = SALIDA / f"{SLUG}_telegram.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final),
                    "-vf", "scale=-2:1280", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "28", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", str(liviano)], check=True)
    minutos = (time.time() - inicio) / 60
    log(f"listo: {completo} ({duracion(final):.0f}s de video, {minutos:.0f} min)")
    telegram(f"🎙️ POC voz {NOMBRE}: {ORIGEN} listo ({duracion(final):.0f} s).\n"
             f"Completo: {completo}", video=liviano)
    return 0


if __name__ == "__main__":
    sys.exit(main())
