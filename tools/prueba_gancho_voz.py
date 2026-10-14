"""Prueba de ganchos (11/10/2026): el mismo gancho con la voz Fish 3 v3 en
varias configuraciones, más el gancho viejo, para elegir de oído.

Por gancho sale un mp3 con las versiones en orden, separadas por un pitido:
  0 = gancho VIEJO, voz como hoy (referencia)
  A = gancho nuevo, voz como hoy (num_step 32, guidance 2.0, velocidad 1.0)
  B = gancho nuevo, guidance 3.0 y velocidad 1.08
  C = gancho nuevo con puntuación dramática (pausas y exclamación), guidance 2.5, velocidad 1.05
  (instruct se probó el 11/10/2026: con voz clonada VoiceStudio responde 500. No sirve.)

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\prueba_gancho_voz.py
"""

import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, r"C:\tts-kokoro\src")
from tts_kokoro.domain.text_normalizer import normalize_text  # noqa: E402

URL = "http://localhost:3900/v1/audio/speech"
VOZ = "cbbc2aa7"
SALIDA = Path(__file__).resolve().parent.parent / "analisis" / "prueba_gancho"
SALIDA.mkdir(parents=True, exist_ok=True)

GANCHOS = {
    "ed_gein": {
        "viejo": "Eres policía en Plainfield, Wisconsin. Es el dieciséis de noviembre de mil novecientos cincuenta y siete, y la dueña de la ferretería desapareció.",
        "nuevo": "La policía entró a su granja y encontró una lámpara hecha con piel humana.",
        "drama": "La policía entró a su granja... y encontró una lámpara. Hecha con piel humana.",
    },
    "amityville": {
        "viejo": "Eres policía en Amityville, Nueva York. Es el trece de noviembre de mil novecientos setenta y cuatro, y te reportan seis muertos en el ciento doce de Ocean Avenue.",
        "nuevo": "Mató a sus padres y a sus cuatro hermanos. Luego dijo que fue la mafia.",
        "drama": "Mató a sus padres. A sus cuatro hermanos. ¡Y luego dijo que fue la mafia!",
    },
    "sinatra": {
        "viejo": "Eres el hijo de uno de los cantantes más famosos del mundo. Tienes diecinueve años, es el ocho de diciembre de mil novecientos sesenta y tres, y estás en el cuarto cuatrocientos diecisiete del hotel Harrah's, en Lake Tahoe.",
        "nuevo": "Frank Sinatra ofreció un millón de dólares por su hijo. Los secuestradores pidieron menos.",
        "drama": "Frank Sinatra ofreció un millón de dólares por su hijo... ¡y los secuestradores pidieron menos!",
    },
    "gasolina_cancun": {
        "viejo": "En Cancún, el litro de Magna ya llegó a veinticinco pesos con treinta y nueve centavos. Y existe un acuerdo para que no pase de veinticuatro.",
        "nuevo": "En Cancún pagas la gasolina más cara que en Monterrey. Y hay un acuerdo para que no pase.",
        "drama": "En Cancún pagas la gasolina más cara que en Monterrey... ¡y hay un acuerdo para que eso no pase!",
    },
}

VERSIONES = [
    ("0", "viejo", {}),
    ("A", "nuevo", {}),
    ("B", "nuevo", {"guidance_scale": 3.0, "speed": 1.08}),
    ("C", "drama", {"guidance_scale": 2.5, "speed": 1.05}),
]


def sintetizar(texto: str, extra: dict, destino: Path) -> None:
    cuerpo = {"model": "omnivoice", "input": normalize_text(texto), "voice": VOZ, "response_format": "wav",
              "language": "es", "num_step": 32, "seed": 1234, **extra}
    r = requests.post(URL, json=cuerpo, timeout=1800)
    r.raise_for_status()
    destino.write_bytes(r.content)


pitido = SALIDA / "_pitido.wav"
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=880:duration=0.25,volume=0.3", "-ar", "24000", "-ac", "1", str(pitido)], check=True)
silencio = SALIDA / "_silencio.wav"
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                "anullsrc=r=24000:cl=mono", "-t", "0.6", str(silencio)], check=True)

for nombre, textos in GANCHOS.items():
    partes = []
    for letra, cual, extra in VERSIONES:
        wav = SALIDA / f"{nombre}_{letra}.wav"
        if not wav.exists():
            sintetizar(textos[cual], extra, wav)
        partes += [silencio, pitido, silencio, wav]
        print(nombre, letra, "listo", flush=True)
    lista = SALIDA / f"{nombre}_lista.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in partes), encoding="utf-8")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-ar", "24000", "-ac", "1", "-b:a", "128k", str(SALIDA / f"{nombre}.mp3")], check=True)
print("ok")
