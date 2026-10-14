"""Crea un perfil de voz por cada toma de una grabación, y los compara.

La grabación es UN archivo con varias tomas separadas por silencios. El script
las corta, arma un perfil de VoiceStudio con cada una y sintetiza la MISMA
frase con todas, para poder elegir de oído.

    python tools/clonar_tomas.py --audio grabacion.wav --guion tomas.json
    python tools/clonar_tomas.py --audio grabacion.wav --guion tomas.json --solo-cortar

`--solo-cortar` deja los fragmentos en disco sin tocar VoiceStudio: sirve para
revisar que el corte haya quedado bien antes de crear nada.

El `ref_text` de cada perfil sale del guion, no de una transcripción
automática: el texto TIENE que coincidir con lo que se dice, y en una toma
corta un error de Whisper arruina la clonación.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import requests
import soundfile as sf

BASE_URL = "http://localhost:3900"

# Lo aprendido clonando la voz del canal: una referencia de 22.4s perdió la
# prueba a ciegas contra una de 7.6s, y la primera de todas fue rechazada por
# el servidor con `clone_ref_too_long`. Más largo no es mejor.
DUR_MIN, DUR_IDEAL, DUR_MAX = 4.0, 8.0, 14.0
SR = 24000


def _log(msg: str) -> None:
    print(msg, flush=True)


def cortar_tomas(audio: Path, esperadas: int, silencio_seg: float = 1.2) -> list[tuple]:
    """Fragmentos de voz separados por silencios largos.

    Se usa un umbral de silencio LARGO (1.2s) a propósito: las pausas naturales
    entre frases son de 0.2-0.5s, así que solo cortan las pausas deliberadas
    que se pidieron entre tomas.
    """
    import librosa

    y, _ = librosa.load(str(audio), sr=SR, mono=True)
    bloques = librosa.effects.split(y, top_db=35, frame_length=1024, hop_length=256)

    # Se pegan los bloques separados por menos de `silencio_seg`: son las
    # pausas de respiración dentro de una misma toma.
    hueco = int(silencio_seg * SR)
    fusionados: list[list[int]] = []
    for a, b in bloques:
        if fusionados and a - fusionados[-1][1] < hueco:
            fusionados[-1][1] = b
        else:
            fusionados.append([a, b])

    # Fuera lo que sea demasiado corto para ser una toma (carraspeos, golpes).
    tomas = [(a, b) for a, b in fusionados if (b - a) / SR >= DUR_MIN]
    _log(f"Detectadas {len(tomas)} toma(s) de las {esperadas} esperadas:")
    for i, (a, b) in enumerate(tomas, 1):
        dur = (b - a) / SR
        aviso = ""
        if dur > DUR_MAX:
            aviso = f"  <- LARGA, se recorta a {DUR_IDEAL:.0f}s"
        _log(f"  {i}: {a/SR:5.1f}s -> {b/SR:5.1f}s  ({dur:4.1f}s){aviso}")
    return [(y, a, b) for a, b in tomas]


def _recortar(y: np.ndarray, a: int, b: int) -> np.ndarray:
    """La toma, acotada a la duración que mejor clona."""
    seg = y[a:b]
    tope = int(DUR_IDEAL * SR)
    if len(seg) <= int(DUR_MAX * SR):
        return seg
    # Se toma del principio: es donde la entonación está más entera, antes de
    # que la frase se apague.
    return seg[:tope]


def crear_perfil(nombre: str, wav: Path, texto: str) -> str | None:
    with wav.open("rb") as f:
        resp = requests.post(
            f"{BASE_URL}/profiles",
            files={"ref_audio": (wav.name, f, "audio/wav")},
            data={"name": nombre, "ref_text": texto, "language": "Spanish", "kind": "clone"},
            timeout=300,
        )
    if not resp.ok:
        _log(f"  FALLÓ ({resp.status_code}): {resp.text[:300]}")
        return None
    datos = resp.json()
    return datos.get("id") or datos.get("profile_id")


def sintetizar(profile_id: str, texto: str, destino: Path) -> bool:
    # response_format wav: sin esto el servidor devuelve MP3 y el archivo queda
    # con extension .wav pero contenido mp3, que confunde a reproductores y a
    # ffmpeg. La API es compatible con OpenAI y respeta este campo.
    resp = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        json={"model": "omnivoice", "voice": profile_id, "input": texto,
              "response_format": "wav"},
        timeout=900,
    )
    if not resp.ok:
        _log(f"  síntesis falló ({resp.status_code}): {resp.text[:200]}")
        return False
    destino.write_bytes(resp.content)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audio", required=True, type=Path, help="grabación con todas las tomas")
    ap.add_argument("--guion", required=True, type=Path,
                    help="JSON con [{nombre, texto}] en el orden de la grabación")
    ap.add_argument("--out", type=Path, default=Path("analisis/voces"))
    ap.add_argument("--solo-cortar", action="store_true",
                    help="corta y sale, sin crear perfiles")
    ap.add_argument("--frase", default="El cuerpo apareció trece días después, "
                                       "en una cisterna que la policía ya había revisado.",
                    help="frase de prueba, la misma para todas las voces")
    args = ap.parse_args()

    if not args.audio.exists():
        _log(f"No existe {args.audio}")
        return 1
    tomas_guion = json.loads(args.guion.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)

    tomas = cortar_tomas(args.audio, len(tomas_guion))
    if len(tomas) != len(tomas_guion):
        _log(f"\nOJO: se esperaban {len(tomas_guion)} tomas y se detectaron {len(tomas)}.")
        _log("Revisá los cortes de arriba. Si están mal, regrabá con pausas más largas")
        _log("entre tomas, o corré con --solo-cortar y ajustá a mano.")
        if not args.solo_cortar:
            return 1

    recortes = []
    for i, ((y, a, b), meta) in enumerate(zip(tomas, tomas_guion), 1):
        seg = _recortar(y, a, b)
        wav = args.out / f"toma{i:02d}_{meta['nombre']}.wav"
        sf.write(str(wav), seg, SR, subtype="PCM_16")
        recortes.append((wav, meta))
        _log(f"  -> {wav.name}  ({len(seg)/SR:.1f}s)")

    if args.solo_cortar:
        _log("\nListo el corte. Escuchá los archivos y volvé a correr sin --solo-cortar.")
        return 0

    _log("\nCreando perfiles...")
    perfiles = []
    for wav, meta in recortes:
        pid = crear_perfil(f"DMG {meta['nombre']}", wav, meta["texto"])
        if pid:
            perfiles.append((pid, meta["nombre"]))
            _log(f"  {meta['nombre']:20} -> {pid}")
        time.sleep(1)

    if not perfiles:
        _log("No se creó ningún perfil.")
        return 1

    _log(f"\nSintetizando la misma frase con las {len(perfiles)} voces...")
    for pid, nombre in perfiles:
        destino = args.out / f"prueba_{nombre}.wav"
        if sintetizar(pid, args.frase, destino):
            _log(f"  {nombre:20} -> {destino.name}")

    _log(f"\nListo. Escuchá los prueba_*.wav en {args.out} y decime cuáles sirven.")
    _log("Los ids de perfil quedan arriba, para ponerlos en el guion por plano.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
