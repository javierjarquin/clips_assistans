"""POC de una voz nueva con los 4 ganchos de la prueba del 11/10/2026.

Por gancho, un mp3 con: Fish 3 "B" (la ganadora) · pitido · voz nueva como
viene · pitido · voz nueva con el ajuste B (guidance 3.0, velocidad 1.08).
Verifica con Whisper que cada versión diga el gancho entero y manda todo
por Telegram.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\poc_voz_nueva_ganchos.py 5f8ed11a
"""

import json
import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, r"C:\tts-kokoro\src")
from tts_kokoro.domain.text_normalizer import normalize_text  # noqa: E402

VOZ = sys.argv[1]
URL = "http://localhost:3900/v1/audio/speech"
RAIZ = Path(__file__).resolve().parent.parent / "analisis"
PREVIA = RAIZ / "prueba_gancho"
SALIDA = RAIZ / f"poc_voz_{VOZ}"
SALIDA.mkdir(parents=True, exist_ok=True)
TELEGRAM = Path(__file__).resolve().parent / "telegram_enviar.py"
WHISPER_PY = r"C:\tts-kokoro\.venv\Scripts\python.exe"

GANCHOS = {
    "ed_gein": "La policía entró a su granja y encontró una lámpara hecha con piel humana.",
    "amityville": "Mató a sus padres y a sus cuatro hermanos. Luego dijo que fue la mafia.",
    "sinatra": "Frank Sinatra ofreció un millón de dólares por su hijo. Los secuestradores pidieron menos.",
    "gasolina_cancun": "En Cancún pagas la gasolina más cara que en Monterrey. Y hay un acuerdo para que no pase.",
}
AJUSTES = {"tal_cual": {}, "B": {"guidance_scale": 3.0, "speed": 1.08}}


def sintetizar(texto, extra, destino):
    cuerpo = {"model": "omnivoice", "input": normalize_text(texto), "voice": VOZ, "response_format": "wav",
              "language": "es", "num_step": 32, "seed": 1234, **extra}
    r = requests.post(URL, json=cuerpo, timeout=1800)
    r.raise_for_status()
    destino.write_bytes(r.content)


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a], check=True)


pitido, silencio = SALIDA / "_pitido.wav", SALIDA / "_silencio.wav"
ff("-f", "lavfi", "-i", "sine=frequency=880:duration=0.25,volume=0.3", "-ar", "24000", "-ac", "1", str(pitido))
ff("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.6", str(silencio))

archivos = []
for nombre, texto in GANCHOS.items():
    partes = [PREVIA / f"{nombre}_B.wav"]
    for etiqueta, extra in AJUSTES.items():
        wav = SALIDA / f"{nombre}_{etiqueta}.wav"
        if not wav.exists():
            sintetizar(texto, extra, wav)
        partes.append(wav)
        print(nombre, etiqueta, "listo", flush=True)
    secuencia = []
    for p in partes:
        secuencia += [silencio, pitido, silencio, p]
    lista = SALIDA / f"{nombre}_lista.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in secuencia), encoding="utf-8")
    mp3 = SALIDA / f"{nombre}.mp3"
    ff("-f", "concat", "-safe", "0", "-i", str(lista), "-ar", "24000", "-ac", "1", "-b:a", "128k", str(mp3))
    archivos.append(mp3)

# -I ignora PYTHONIOENCODING: la salida se fuerza a UTF-8 dentro del código.
codigo = ("import glob,json,sys\nsys.stdout.reconfigure(encoding='utf-8')\n"
          "from faster_whisper import WhisperModel\n"
          "m=WhisperModel('small',device='cpu',compute_type='int8')\n"
          f"print(json.dumps({{f.split(chr(92))[-1]: ' '.join(s.text.strip() for s in m.transcribe(f,language='es')[0]) "
          f"for f in sorted(glob.glob(r'{SALIDA}\\*_tal_cual.wav')+glob.glob(r'{SALIDA}\\*_B.wav'))}}, ensure_ascii=False))")
import os  # noqa: E402
out = subprocess.run([WHISPER_PY, "-I", "-c", codigo], capture_output=True, text=True, encoding="utf-8",
                     env={**os.environ, "PYTHONIOENCODING": "utf-8"}).stdout
oido = json.loads(out.strip().splitlines()[-1])
reporte = "\n".join(f"{k}: {v}" for k, v in oido.items())
(SALIDA / "whisper.txt").write_text(reporte, encoding="utf-8")
print(reporte)

if "--sin-telegram" not in sys.argv:
    py = sys.executable
    subprocess.run([py, str(TELEGRAM),
                    "POC TU VOZ NUEVA (ganchos). Cada audio trae 3 versiones separadas por un pitido:\n"
                    "1 = Fish 3 con el ajuste B (la que elegiste)\n"
                    "2 = TU VOZ nueva, tal cual\n"
                    "3 = TU VOZ nueva con el ajuste B (un poco mas rapida y pegada a la voz)\n"
                    "Dime cual te atrapa mas en cada uno."])
    for mp3 in archivos:
        subprocess.run([py, str(TELEGRAM), f"Gancho: {mp3.stem}", str(mp3)])
