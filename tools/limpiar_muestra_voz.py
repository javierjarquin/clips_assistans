"""Limpieza cuidadosa de una muestra de voz para clonar (11/10/2026).

La supresión de ruido en vivo (AMD, la del micrófono) se comía consonantes:
"esa" sonaba "hacia", "ladraba" sonaba "la daba". Aquí se graba SIN supresión
y se limpia después, sabiendo qué es ruido:

1. Huella del ruido: el espectro promedio del silencio del inicio (el cuarto).
2. Resta espectral SUAVE: a cada frecuencia se le quita esa huella, pero con
   un tope (`--max-db`, por defecto 12 dB): nunca se apaga una banda entera,
   que es lo que borra las "s" y las "r" suaves.
3. Filtro de graves (70 Hz) y ganancia fija hasta un pico de -1.5 dB, sin
   compresión: la dinámica (la emoción) queda como la grabaste.

    .venv\\Scripts\\python.exe tools\\limpiar_muestra_voz.py entrada.wav salida.wav \\
        [--ruido 0.5:4.5] [--max-db 12]
"""

import argparse

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ap = argparse.ArgumentParser()
ap.add_argument("entrada")
ap.add_argument("salida")
ap.add_argument("--ruido", default="0.5:4.5", help="segundos de silencio para la huella")
ap.add_argument("--max-db", type=float, default=12.0, help="lo máximo que se baja una frecuencia")
args = ap.parse_args()

y, sr = sf.read(args.entrada, dtype="float32")
if y.ndim > 1:
    y = y.mean(axis=1)
y = sosfilt(butter(4, 70, "highpass", fs=sr, output="sos"), y)

N, H = 2048, 512
S = librosa.stft(y, n_fft=N, hop_length=H)
mag, fase = np.abs(S), np.angle(S)
a, b = (float(x) for x in args.ruido.split(":"))
cuadros = slice(int(a * sr / H), int(b * sr / H))
huella = np.median(mag[:, cuadros], axis=1, keepdims=True)

# Ganancia por celda: lo que queda tras restar 1.5 veces la huella, con un piso
# que respeta el tope de reducción. Se suaviza en el tiempo para que no "burbujee".
piso = 10 ** (-args.max_db / 20)
ganancia = np.clip((mag - 1.5 * huella) / np.maximum(mag, 1e-9), piso, 1.0)
k = 5
ganancia = np.apply_along_axis(lambda g: np.convolve(g, np.ones(k) / k, mode="same"), 1, ganancia)
limpio = librosa.istft(ganancia * mag * np.exp(1j * fase), hop_length=H, length=len(y))

pico = np.max(np.abs(limpio))
limpio = limpio * (10 ** (-1.5 / 20) / pico)
sf.write(args.salida, limpio, sr, subtype="PCM_16")
print(f"listo: {args.salida} (ganancia {20 * np.log10(10 ** (-1.5 / 20) / pico):+.1f} dB, tope {args.max_db} dB)")
