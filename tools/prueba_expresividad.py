"""¿De dónde sale lo plano de la voz de producción, y qué lo mejora?

Sintetiza las mismas frases de true crime con variantes de VoiceStudio y mide
en cada una la variación de entonación (desvío del tono en semitonos: una voz
que "no sube ni baja" da poco) y el ritmo. Las variantes cambian UNA cosa por
vez contra la línea base, para saber qué pesa.

    .venv\\Scripts\\python.exe tools\\prueba_expresividad.py            # sintetiza y mide
    .venv\\Scripts\\python.exe tools\\prueba_expresividad.py --medir    # solo mide lo que hay

Salida en analisis/expresividad/.
"""

import argparse
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "http://localhost:3900/v1/audio/speech"
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "expresividad"
PRODUCCION = "95e2570b"

# Tierra Blanca (lote del 26/09/2026): el gancho y el plano de "el hecho".
FRASES = {
    "gancho": "Una cámara grabó a policías deteniendo a cinco jóvenes. "
              "Un vocero estatal dijo que eso nunca pasó.",
    "hecho": "El video mostraba las mismas patrullas que el comandante había negado "
             "esa tarde. Varios policías aparecían subiendo a los jóvenes a la fuerza.",
}
# El mismo texto con puntuación de narrador: pausa antes de la palabra que pega.
DRAMATICAS = {
    "gancho": "Una cámara grabó a policías… deteniendo a cinco jóvenes. "
              "Un vocero estatal dijo que eso… nunca pasó.",
    "hecho": "El video mostraba las mismas patrullas. Las que el comandante había negado "
             "esa tarde. Varios policías… subiendo a los jóvenes. A la fuerza.",
}

VARIANTES = {
    "a_base": {},
    "b_calidad32": {"num_step": 32},
    "c_puntuacion": {"_texto": DRAMATICAS},
    "d_lento": {"speed": 0.9},
    "e_guidance3": {"guidance_scale": 3.0},
    # Otra referencia, leída con actuación (la tercera voz): mide cuánto pesa
    # la referencia contra los parámetros.
    "f_ref_actuada": {"voice": "d1cc4bf2"},
    # Referencia de narrador de terror generada en Fish Audio (28/09/2026).
    "g_fish": {"voice": "362843f0"},
    "h_fish_calidad32": {"voice": "362843f0", "num_step": 32},
    # Segunda voz de Fish (28/09/2026), por defecto y con el ajuste de B.
    "i_fish2": {"voice": "746b6e2d"},
    "j_fish2_calidad32": {"voice": "746b6e2d", "num_step": 32},
}


def sintetizar(variante: str, extra: dict) -> None:
    textos = extra.pop("_texto", FRASES)
    for clave, texto in textos.items():
        destino = SALIDA / f"{variante}_{clave}.wav"
        if destino.exists():
            continue
        cuerpo = {"model": "omnivoice", "voice": PRODUCCION, "input": texto,
                  "response_format": "wav", "seed": 7, **extra}
        r = requests.post(URL, json=cuerpo, timeout=1800)
        r.raise_for_status()
        destino.write_bytes(r.content)
        print(f"  {destino.name}", flush=True)


def medir(ruta: Path, palabras: int | None) -> dict:
    y, sr = librosa.load(ruta, sr=16000, mono=True)
    f0, voz, _ = librosa.pyin(y, fmin=65, fmax=350, sr=sr)
    f0 = f0[voz & ~np.isnan(f0)]
    semitonos = 12 * np.log2(f0 / np.median(f0))
    dur = len(y) / sr
    # Pausas: tramos de más de 150 ms por debajo de -40 dB respecto del pico.
    rms = librosa.feature.rms(y=y, frame_length=400, hop_length=160)[0]
    db = librosa.amplitude_to_db(rms, ref=np.max)
    silencio = db < -40
    pausas, corrida = 0, 0
    for s in silencio:
        corrida = corrida + 1 if s else 0
        pausas += corrida == 15  # 15 cuadros de 10 ms = 150 ms
    return {
        "dur": round(dur, 1),
        "tono_hz": round(float(np.median(f0)), 0),
        "variacion_st": round(float(np.std(semitonos)), 2),
        "rango_st": round(float(np.percentile(semitonos, 95) - np.percentile(semitonos, 5)), 1),
        "ppm": round(palabras / dur * 60) if palabras else None,
        "pausas": int(pausas),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--medir", action="store_true")
    args = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)

    if not args.medir:
        for nombre, extra in VARIANTES.items():
            print(f"{nombre}...", flush=True)
            sintetizar(nombre, dict(extra))

    filas = {}
    ref = Path(__file__).resolve().parents[1] / "analisis" / "ref_voz_javier.wav"
    filas["referencia_de_la_voz"] = medir(ref, None)
    ref3 = Path(__file__).resolve().parents[1] / "analisis" / "mivoz" / "referencia_blas.wav"
    if ref3.exists():
        filas["referencia_actuada"] = medir(ref3, None)
    ref4 = Path(__file__).resolve().parents[1] / "analisis" / "voz_fish" / "referencia_fish.wav"
    if ref4.exists():
        filas["referencia_fish"] = medir(ref4, None)
    ref5 = Path(__file__).resolve().parents[1] / "analisis" / "voz_fish2" / "referencia_fish2.wav"
    if ref5.exists():
        filas["referencia_fish2"] = medir(ref5, None)
    for ruta in sorted(SALIDA.glob("*.wav")):
        clave = ruta.stem.rsplit("_", 1)[1]
        filas[ruta.stem] = medir(ruta, len(FRASES[clave].split()))

    print(f"\n{'':24}{'dur':>6}{'tono':>6}{'variac':>8}{'rango':>7}{'ppm':>6}{'pausas':>7}")
    for nombre, m in filas.items():
        print(f"{nombre:24}{m['dur']:>6}{m['tono_hz']:>6.0f}{m['variacion_st']:>8}"
              f"{m['rango_st']:>7}{m['ppm'] or '':>6}{m['pausas']:>7}")
    (SALIDA / "medidas.json").write_text(json.dumps(filas, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
