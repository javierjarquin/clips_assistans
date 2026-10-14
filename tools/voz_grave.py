"""Baja el tono de la voz clonada del canal y arma la comparación.

Hay dos formas de conseguir una voz más grave, y suenan distinto:

  A. Post-proceso: se sintetiza normal con el perfil de producción y se le
     baja el tono al wav resultante. Hay que aplicarlo a cada audio generado.
  B. Referencia grave: se le baja el tono a la REFERENCIA y se clona un perfil
     nuevo desde ahí. El TTS ya sale grave, sin post-proceso.

    python tools/voz_grave.py                 # arma todo y deja los wav para comparar
    python tools/voz_grave.py --solo-a        # solo el post-proceso (no toca VoiceStudio)

`rubberband` con `formant=preserved` mantiene el tracto vocal donde estaba y
solo mueve el tono: sin eso la voz suena a alguien mucho más grande, el efecto
"barril". Es la diferencia entre sonar grave y sonar procesado.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import requests

BASE_URL = "http://localhost:3900"
PERFIL_PROD = "95e2570b"
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "analisis" / "voz_grave"
REFERENCIA = RAIZ / "analisis" / "_ref_95e2570b.wav"

# Medido sobre la referencia de producción y sobre la voz grave de ejemplo:
# 154 Hz -> 105 Hz son 6.7 semitonos. Se prueban tres escalones porque el
# máximo no siempre es el que suena mejor: cuanto más se baja, más se nota.
SEMITONOS = (4.0, 5.5, 6.7)

FRASE = ("El cuerpo apareció trece días después, en una cisterna que la "
         "policía ya había revisado.")


def _log(msg: str) -> None:
    print(msg, flush=True)


def bajar_tono(origen: Path, destino: Path, semitonos: float,
               formantes: bool = True) -> None:
    factor = 2 ** (-semitonos / 12)
    modo = "preserved" if formantes else "shifted"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(origen),
         "-af", f"rubberband=pitch={factor:.6f}:formant={modo}", str(destino)],
        check=True,
    )


def sintetizar(profile_id: str, texto: str, destino: Path) -> bool:
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


def crear_perfil(nombre: str, wav: Path, texto: str) -> str | None:
    with wav.open("rb") as f:
        resp = requests.post(
            f"{BASE_URL}/profiles",
            files={"ref_audio": (wav.name, f, "audio/wav")},
            data={"name": nombre, "ref_text": texto, "language": "Spanish",
                  "kind": "clone"},
            timeout=300,
        )
    if not resp.ok:
        _log(f"  perfil falló ({resp.status_code}): {resp.text[:300]}")
        return None
    datos = resp.json()
    return datos.get("id") or datos.get("profile_id")


def medir(wav: Path) -> str:
    import librosa
    import numpy as np

    y, sr = librosa.load(str(wav), sr=24000, mono=True)
    f0, _, _ = librosa.pyin(y, fmin=50, fmax=300, sr=sr, frame_length=1024)
    v = f0[~np.isnan(f0)]
    if not len(v):
        return "sin voz detectada"
    palabras = len(FRASE.split())
    wpm = palabras / (len(y) / sr) * 60
    return f"{np.median(v):5.0f} Hz   {len(y)/sr:4.1f}s   {wpm:3.0f} ppm"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--solo-a", action="store_true",
                    help="solo el post-proceso, sin crear perfiles")
    ap.add_argument("--frase", default=FRASE)
    ap.add_argument("--referencia", type=Path, default=REFERENCIA,
                    help="wav de referencia del que clonar")
    ap.add_argument("--texto", type=Path,
                    help="archivo con el ref_text literal de esa referencia")
    ap.add_argument("--semitonos", type=str,
                    help="lista separada por comas, p.ej. 0,1.5,3")
    ap.add_argument("--etiqueta", default="",
                    help="prefijo para no pisar una comparación anterior")
    args = ap.parse_args()

    SALIDA.mkdir(parents=True, exist_ok=True)
    referencia = args.referencia
    texto_ref = args.texto or (SALIDA / "ref_text.txt")
    ref_text = texto_ref.read_text(encoding="utf-8").strip()
    semitonos = ([float(x) for x in args.semitonos.split(",")]
                 if args.semitonos else list(SEMITONOS))
    pre = f"{args.etiqueta}_" if args.etiqueta else ""

    _log("CAMINO A — post-proceso sobre la salida del perfil actual")
    base = SALIDA / f"{pre}a_00_original.wav"
    if not base.exists() and not sintetizar(PERFIL_PROD, args.frase, base):
        return 1
    hechos = [base]
    for st in semitonos:
        if not st:
            continue
        dest = SALIDA / f"{pre}a_{str(st).replace('.', '_')}st.wav"
        bajar_tono(base, dest, st)
        hechos.append(dest)

    if args.solo_a:
        _log("")
        for wav in hechos:
            _log(f"  {wav.name:24} {medir(wav)}")
        return 0

    _log("\nCAMINO B — perfil clonado desde la referencia ya grave")
    perfiles = {}
    registro = SALIDA / f"{pre}perfiles_graves.json"
    if registro.exists():
        perfiles = json.loads(registro.read_text(encoding="utf-8"))

    for st in semitonos:
        clave = f"{st}st"
        if clave in perfiles:
            _log(f"  {clave:8} ya existía -> {perfiles[clave]}")
            continue
        ref_grave = SALIDA / f"{pre}ref_{str(st).replace('.', '_')}st.wav"
        if st:
            bajar_tono(referencia, ref_grave, st)
        else:
            # 0 semitonos: la referencia tal cual, sin tocar. Es el control que
            # dice cuánto del resultado viene del tramo elegido y cuánto del
            # procesamiento.
            ref_grave.write_bytes(referencia.read_bytes())
        pid = crear_perfil(f"DMG {args.etiqueta or 'grave'} -{st}st", ref_grave, ref_text)
        if not pid:
            continue
        perfiles[clave] = pid
        _log(f"  {clave:8} -> {pid}")
        registro.write_text(json.dumps(perfiles, indent=2), encoding="utf-8")

    for clave, pid in perfiles.items():
        dest = SALIDA / f"{pre}b_{clave.replace('.', '_')}.wav"
        if not dest.exists():
            sintetizar(pid, args.frase, dest)
        hechos.append(dest)

    _log("\nMedición de todo lo generado:")
    for wav in hechos:
        if wav.exists():
            _log(f"  {wav.name:24} {medir(wav)}")
    _log(f"\nListo. Los wav están en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
