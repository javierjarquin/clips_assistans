"""Puntúa grabaciones de voz reales para elegir cuál sirve de referencia de clonado.

    python tools/elegir_referencia.py archivo1.wav archivo2.m4a ...
    python tools/elegir_referencia.py --ventana 8 archivo.wav   # además busca el mejor tramo

No mide "qué tan linda" es la voz: mide lo que arruina una clonación. Por orden
de daño real, según lo que ya nos pasó en este proyecto:

  ruido de fondo   el modelo clona la sala junto con la voz
  recorte (clip)   la distorsión se aprende como timbre
  reverb           la voz sale "dentro" de un cuarto y no se puede sacar después
  ritmo rápido     la voz clonada hereda las palabras por minuto de la referencia
  tono inestable   una referencia con mucha variación le da un objetivo borroso

El puntaje es 0-100 y está ponderado con esas prioridades. Sirve para ordenar
candidatos, no como nota absoluta.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

SR = 24000


def _cargar(ruta: Path) -> np.ndarray:
    """Audio mono a 24 kHz, decodificando con ffmpeg lo que librosa no abre bien."""
    import librosa

    if ruta.suffix.lower() in (".wav", ".flac"):
        y, _ = librosa.load(str(ruta), sr=SR, mono=True)
        return y
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(ruta),
                        "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        y, _ = librosa.load(str(wav), sr=SR, mono=True)
        return y


def _db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-9))


def analizar(y: np.ndarray) -> dict:
    import librosa

    dur = len(y) / SR
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
    # El piso de ruido se toma del percentil 5 de la energía por trama: son las
    # pausas entre frases. El nivel de voz, del percentil 90 (no del máximo,
    # que lo fija cualquier golpe de micrófono).
    ruido, voz = _db(np.percentile(rms, 5)), _db(np.percentile(rms, 90))

    f0, sonoro, _ = librosa.pyin(y, fmin=50, fmax=300, sr=SR, frame_length=1024)
    v = f0[~np.isnan(f0)]
    tono = float(np.median(v)) if len(v) else 0.0
    # La dispersión se mide en semitonos y no en Hz: 20 Hz arriba de 100 no es
    # lo mismo que 20 Hz arriba de 200.
    disp = float(np.std(12 * np.log2(v / tono))) if len(v) > 10 else 0.0

    recorte = float(np.mean(np.abs(y) > 0.99))
    densidad = float(np.mean(sonoro > 0.5))

    # Ancho de banda real: hasta dónde llega la energía. Un archivo muy
    # comprimido corta arriba de 8-10 kHz y eso se oye como "teléfono".
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    acum = np.cumsum(S.mean(axis=1))
    banda = float(np.searchsorted(acum, acum[-1] * 0.99) * SR / 2048)

    return {"dur": dur, "ruido": ruido, "voz": voz, "snr": voz - ruido,
            "tono": tono, "disp": disp, "recorte": recorte,
            "densidad": densidad, "banda": banda}


def puntuar(m: dict) -> float:
    """0-100, ponderado por cuánto daña cada defecto a la clonación."""
    # SNR: por debajo de 25 dB el ruido entra al perfil; arriba de 45 ya da igual.
    snr = np.clip((m["snr"] - 25) / 20, 0, 1) * 35
    # Recorte: es el defecto que menos perdón tiene, se penaliza duro.
    clip = (1 - np.clip(m["recorte"] * 200, 0, 1)) * 20
    # Ancho de banda: 8 kHz o más está bien para voz.
    banda = np.clip((m["banda"] - 5000) / 3000, 0, 1) * 15
    # Dispersión de tono: 1.5-3.5 semitonos es habla expresiva pero estable.
    disp = (1 - np.clip(abs(m["disp"] - 2.5) / 2.5, 0, 1)) * 15
    # Densidad de voz: mucho silencio en la referencia desperdicia el fragmento.
    dens = np.clip((m["densidad"] - 0.3) / 0.4, 0, 1) * 15
    return float(snr + clip + banda + disp + dens)


def mejor_ventana(y: np.ndarray, seg: float, paso_seg: float = 0.5,
                  cuantos: int = 1) -> list[tuple[float, float]]:
    """Los `cuantos` mejores tramos de `seg` segundos, sin solaparse entre sí."""
    n, paso = int(seg * SR), int(paso_seg * SR)
    if len(y) <= n:
        return [(0.0, puntuar(analizar(y)))]
    puntos = [(puntuar(analizar(y[i:i + n])), i)
              for i in range(0, len(y) - n, paso)]
    elegidos: list[tuple[float, float]] = []
    for pt, ini in sorted(puntos, reverse=True):
        # Sin solape: dos tramos casi iguales no son dos opciones.
        if any(abs(ini / SR - otro) < seg for otro, _ in elegidos):
            continue
        elegidos.append((ini / SR, pt))
        if len(elegidos) >= cuantos:
            break
    return elegidos


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archivos", nargs="+", type=Path)
    ap.add_argument("--ventana", type=float, default=0.0,
                    help="segundos; si se pasa, busca el mejor tramo de cada archivo")
    ap.add_argument("--paso", type=float, default=0.5,
                    help="resolución de la búsqueda de tramo, en segundos")
    ap.add_argument("--cuantos", type=int, default=1,
                    help="cuántos tramos listar por archivo")
    args = ap.parse_args()

    print(f"{'archivo':38} {'dur':>6} {'SNR':>6} {'tono':>6} {'disp':>5} "
          f"{'banda':>6} {'clip':>6} {'dens':>5} {'pts':>5}")
    filas = []
    for ruta in args.archivos:
        if not ruta.exists():
            print(f"{ruta.name:38}  no existe")
            continue
        m = analizar(_cargar(ruta))
        pt = puntuar(m)
        filas.append((pt, ruta, m))
        print(f"{ruta.name[:38]:38} {m['dur']:5.0f}s {m['snr']:5.1f}dB "
              f"{m['tono']:5.0f}Hz {m['disp']:4.1f}st {m['banda']/1000:5.1f}k "
              f"{m['recorte']*100:5.2f}% {m['densidad']*100:4.0f}% {pt:5.1f}")

    if args.ventana and filas:
        print(f"\nMejor tramo de {args.ventana:.0f}s en cada archivo:")
        for _, ruta, _ in sorted(filas, reverse=True, key=lambda f: f[0]):
            for ini, pt in mejor_ventana(_cargar(ruta), args.ventana,
                                         args.paso, args.cuantos):
                print(f"  {ruta.name[:38]:38} desde {ini:6.1f}s   pts {pt:5.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
