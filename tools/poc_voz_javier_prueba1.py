"""PoC de la voz dramática de Javier con la PRIMERA toma (11/10/2026).

De las seis tomas de hoy (PRUEBA1..test6) Javier eligió de oído la primera.
Acá se clona un perfil de VoiceStudio con ella y se sintetiza la misma frase
con las dos duraciones de referencia que quedaron cortadas, más la voz actual
del canal (Fish 3 v3) como punto de comparación.

Se clona del audio CRUDO, no de la versión "arreglada": la limpieza se come
consonantes (ver limpiar_muestra_voz.py) y para la referencia importa más la
entonación entera que el ruido de fondo del cuarto.

Sale un mp3 con las tres versiones en orden, separadas por un pitido, igual
que la prueba de ganchos:
  1 = Javier, referencia de 10.6 s
  2 = Javier, referencia de 14.6 s
  3 = Fish 3 v3 (la voz de los true crime hoy)

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\poc_voz_javier_prueba1.py [--sin-telegram]
"""

import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, r"C:\tts-kokoro\src")
from tts_kokoro.domain.text_normalizer import normalize_text  # noqa: E402

BASE_URL = "http://localhost:3900"
BOT_PY = r"C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
TELEGRAM = Path(__file__).resolve().parent / "telegram_enviar.py"

MUESTRAS = Path(__file__).resolve().parent.parent / "analisis" / "voz_javier_dramatica"
SALIDA = Path(__file__).resolve().parent.parent / "analisis" / "poc_voz_javier_prueba1"

# `ref_text` escrito a mano contra lo que transcribió Whisper de ESTOS cortes
# (no de otra toma del mismo guion): con una referencia corta, una palabra que
# no coincide arruina la clonación.
_T10 = ("La policía entró a la casa y encontró algo que nadie esperaba. Eran las tres de la "
        "mañana, seis personas, una sola familia. ¿Quién fue? Durante años nadie dijo nada.")
_T14 = _T10[:-1] + (", hasta que la señora Juárez corrió hacia la calle, gritando en la noche.")

REFERENCIAS = [
    ("1", "Javier PRUEBA1 10s", MUESTRAS / "prueba1_crudo_10s.wav", _T10),
    ("2", "Javier PRUEBA1 14s", MUESTRAS / "prueba1_crudo_14s.wav", _T14),
]

# La voz de los true crime hoy, para oír la diferencia en la misma frase.
FISH3 = ("3", "Fish 3 v3 (voz actual)", "cbbc2aa7")

# La frase de prueba de clonar_tomas.py, más el cierre del canal: nunca es el
# texto de la referencia, así se oye la voz diciendo algo que no "copió".
FRASE = ("El cuerpo apareció trece días después, en una cisterna que la policía ya había "
         "revisado. Y aquí, el dato mata al gato.")

NUM_STEP = 32   # lo que usan los true crime en producción
SEMILLA = 1234  # misma semilla en las tres: que solo cambie la voz


def log(msg: str) -> None:
    print(msg, flush=True)


def ff(*args) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def perfiles_existentes() -> dict[str, str]:
    r = requests.get(f"{BASE_URL}/profiles", timeout=60)
    r.raise_for_status()
    return {p["name"]: p["id"] for p in r.json()}


def crear_perfil(nombre: str, wav: Path, texto: str) -> str:
    with wav.open("rb") as f:
        r = requests.post(
            f"{BASE_URL}/profiles",
            files={"ref_audio": (wav.name, f, "audio/wav")},
            data={"name": nombre, "ref_text": texto, "language": "Spanish", "kind": "clone"},
            timeout=300,
        )
    if not r.ok:
        raise SystemExit(f"No se pudo crear el perfil {nombre!r} ({r.status_code}): {r.text[:300]}")
    datos = r.json()
    return datos.get("id") or datos["profile_id"]


def sintetizar(profile_id: str, texto: str, destino: Path) -> None:
    r = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        json={"model": "omnivoice", "voice": profile_id, "input": normalize_text(texto),
              "response_format": "wav", "language": "es", "num_step": NUM_STEP, "seed": SEMILLA},
        timeout=1800,
    )
    if not r.ok:
        raise SystemExit(f"La síntesis falló ({r.status_code}): {r.text[:300]}")
    destino.write_bytes(r.content)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    ya = perfiles_existentes()

    voces = []
    for letra, nombre, wav, texto in REFERENCIAS:
        if not wav.exists():
            raise SystemExit(f"Falta la referencia {wav}")
        pid = ya.get(nombre) or crear_perfil(nombre, wav, texto)
        log(f"{letra}: {nombre:22} -> perfil {pid}" + ("  (ya existía)" if nombre in ya else ""))
        voces.append((letra, nombre, pid))
    voces.append(FISH3)

    pitido, silencio = SALIDA / "_pitido.wav", SALIDA / "_silencio.wav"
    ff("-f", "lavfi", "-i", "sine=frequency=880:duration=0.25,volume=0.3",
       "-ar", "24000", "-ac", "1", str(pitido))
    ff("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.6", str(silencio))

    partes = []
    for letra, nombre, pid in voces:
        wav = SALIDA / f"{letra}_{pid}.wav"
        if not wav.exists():
            log(f"sintetizando {letra} ({nombre})...")
            sintetizar(pid, FRASE, wav)
        partes += [silencio, pitido, silencio, wav]
        log(f"  {letra} listo: {wav.name}")

    lista = SALIDA / "_lista.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in partes), encoding="utf-8")
    mp3 = SALIDA / "comparacion.mp3"
    ff("-f", "concat", "-safe", "0", "-i", str(lista), "-ar", "24000", "-ac", "1", "-b:a", "160k",
       str(mp3))
    log(f"\nListo: {mp3}")
    for letra, nombre, pid in voces:
        log(f"  pitido {letra} -> {nombre} ({pid})")

    if "--sin-telegram" not in sys.argv:
        texto = ("PoC de tu voz dramatica con la PRIMERA toma (PRUEBA1). Misma frase, tres voces, "
                 "separadas por un pitido: 1) tu voz con referencia de 10.6s, 2) tu voz con "
                 "referencia de 14.6s, 3) Fish 3, la voz de los true crime hoy. Decime cual.")
        subprocess.run([BOT_PY, str(TELEGRAM), texto, str(mp3)], check=False)


if __name__ == "__main__":
    main()
