"""POC: el Huay Chivo narrado con la tercera voz (perfil d1cc4bf2 de VoiceStudio).

Trabaja sobre una COPIA del mito (slug mito-huay-chivo-voz3): mismo guion y
mismas imágenes, solo cambia la voz, así el original queda para comparar.
Rehace audio, alineación y ensamblado igual que tools/regenerar_voz.py del bot.

Al final avisa por Telegram con una versión liviana del video (el bot de
Telegram no acepta más de 50 MB y el final pesa ~130).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\poc_tercera_voz.py
"""

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

# ANTES de cargar el .env: load_dotenv no pisa lo que ya está en el entorno,
# así el perfil de producción (95e2570b) queda intacto en el .env.
os.environ["VOICESTUDIO_VOICE_ID"] = "d1cc4bf2"
os.environ["TTS_ENGINE"] = "voicestudio"

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BOT / ".env")

import requests  # noqa: E402

from dato_mata_gato_bot import pipeline  # noqa: E402

ORIGEN = "mito-huay-chivo"
SLUG = "mito-huay-chivo-voz3"
SALIDA = Path(r"C:\Android_in\lotes\poc-tercera-voz")
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
    log(f"copiando {ORIGEN} -> {SLUG}")
    copiar(pipeline.ANDROID_IN / ORIGEN, pipeline.ANDROID_IN / SLUG)
    # Imágenes y medios se reusan; lo que depende de la voz vieja NO se copia.
    copiar(pipeline.NARRATOR_PROJECTS / ORIGEN, pipeline.NARRATOR_PROJECTS / SLUG,
           sin=("final.mp4", "narracion.wav", "transcript.json", "planos_alineados.json",
                "visemas.json", "captions.ass", "clips", "_silencios", "hoja_de_contacto.jpg"))
    pipeline._stage_guion_for_tts(SLUG)

    falta = pipeline.motor_tts_listo()
    if falta:
        telegram(f"POC tercera voz: no arrancó. {falta}")
        log(falta)
        return 1

    telegram("POC tercera voz: arranqué con el Huay Chivo (mismo guion e imágenes, "
             "solo cambia la voz). Te aviso cuando esté.")
    inicio = time.time()
    log("sintetizando con el perfil d1cc4bf2")
    ok, out = pipeline._generate_audio(SLUG, "am_adam")
    if not ok:
        telegram(f"POC tercera voz: falló la voz.\n{out[-600:]}")
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
        telegram(f"POC tercera voz: falló el armado del video.\n{out[-600:]}")
        log(out)
        return 1

    SALIDA.mkdir(parents=True, exist_ok=True)
    completo = SALIDA / "huaychivo_tercera_voz.mp4"
    shutil.copy2(final, completo)
    liviano = SALIDA / "huaychivo_tercera_voz_telegram.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final),
                    "-vf", "scale=-2:1280", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "28", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", str(liviano)], check=True)
    minutos = (time.time() - inicio) / 60
    log(f"listo: {completo} ({duracion(final):.0f}s de video, {minutos:.0f} min)")
    telegram(f"🎙️ POC tercera voz: Huay Chivo listo ({duracion(final):.0f} s).\n"
             f"Completo: {completo}\n"
             f"Original para comparar: C:\\illustrated-narrator\\projects\\{ORIGEN}\\final.mp4",
             video=liviano)
    return 0


if __name__ == "__main__":
    sys.exit(main())
