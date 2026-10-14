"""POC: video completo de un true crime con evidencia real y SIN imágenes de IA.

Corre el pipeline del bot tal cual (voz de true crime, logo fijo) con el
generador de imágenes APAGADO (NARR_IMAGE_BACKEND=none): si una toma se queda
sin evidencia, el video falla en vez de rellenarla con IA. Al final lo manda
por Telegram en versión liviana.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\poc_evidencia_video.py <slug>
"""

import os
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BOT = Path(r"C:\dato-mata-gato-bot")
sys.path.insert(0, str(BOT / "src"))
# Sin tocar NARR_IMAGE_BACKEND acá (29/09/2026): desde que el pipeline arma la
# evidencia, es él el que apaga la IA para un guion con "evidencia". Si esta
# prueba sale con alguna imagen de IA, el que falla es el pipeline.

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BOT / ".env")

import requests  # noqa: E402

from dato_mata_gato_bot import pipeline  # noqa: E402

SLUG = sys.argv[1]
SALIDA = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(r"C:\Android_in\lotes\poc-evidencia")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")[0].strip()


def telegram(texto: str, video: Path | None = None) -> None:
    try:
        if video is None:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          data={"chat_id": CHAT, "text": texto}, timeout=30)
        else:
            with open(video, "rb") as f:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                              data={"chat_id": CHAT, "caption": texto,
                                    "supports_streaming": "true"},
                              files={"video": f}, timeout=600)
    except Exception as exc:  # noqa: BLE001
        print("no se pudo avisar por Telegram:", exc, flush=True)


inicio = time.time()
telegram(f"POC evidencia real: arranqué '{SLUG}' (voz Fish 3, logo fijo, sin IA).")
r = pipeline.run(SLUG, "am_adam", destino_local=SALIDA)
print(("OK " if r.ok else "FALLÓ ") + r.mensaje[-1500:], flush=True)
if r.ok:
    final = pipeline.NARRATOR_PROJECTS / SLUG / "final.mp4"
    liviano = SALIDA / f"{SLUG}_telegram.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final),
                    "-vf", "scale=-2:1280", "-c:v", "libx264", "-crf", "28",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(liviano)],
                   check=True)
    telegram(f"🎬 POC evidencia real listo ({(time.time() - inicio) / 60:.0f} min).", liviano)
else:
    telegram(f"POC evidencia real falló:\n{r.mensaje[-600:]}")
