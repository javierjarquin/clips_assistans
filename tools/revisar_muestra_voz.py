"""Revisa una toma de voz de Javier para clonar (11/10/2026) y la manda a Telegram.

Mide nivel, ruido en las pausas, pausas, transcripción palabra por palabra
(Whisper small, marcando las dudosas), arregla el audio (filtro de graves,
reducción suave de ruido, normalización a -18 LUFS) y recorta el tramo para
clonar: de "La policía" hasta "familia".

Corre con el venv de clip_assistance (librosa) y llama a Whisper con el de
tts-kokoro (faster-whisper):

    .venv\\Scripts\\python.exe tools\\revisar_muestra_voz.py PRUEBA3 [--sin-telegram]
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np

ORIGEN = Path(r"C:\Users\jarqu\OneDrive\Documentos\Audacity")
CARPETA = Path(__file__).resolve().parent.parent / "analisis" / "voz_javier_dramatica"
WHISPER_PY = r"C:\tts-kokoro\.venv\Scripts\python.exe"
BOT_PY = r"C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
TELEGRAM = Path(__file__).resolve().parent / "telegram_enviar.py"
FISH3 = Path(__file__).resolve().parent.parent / "analisis" / "voz_fish3_v3" / "referencia_v3.wav"

nombre = sys.argv[1]
CARPETA.mkdir(parents=True, exist_ok=True)
crudo = CARPETA / f"{nombre}.wav"
crudo.write_bytes((ORIGEN / f"{nombre}.wav").read_bytes())
arreglada = CARPETA / f"{nombre}_arreglada.wav"
tramo = CARPETA / f"{nombre}_tramo_para_clonar.wav"


def ff(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stderr


def nivel(ruta, a=None, b=None):
    filtro = (f"atrim={a}:{b}," if a is not None else "") + "astats=metadata=0"
    err = ff("-i", str(ruta), "-af", filtro, "-f", "null", "-")
    pico = float(re.search(r"Peak level dB: (-?[\d.inf]+)", err).group(1))
    rms = float(re.search(r"RMS level dB: (-?[\d.inf]+)", err).group(1))
    return pico, rms


def pausas(ruta):
    err = ff("-i", str(ruta), "-af", "silencedetect=noise=-50dB:d=0.35", "-f", "null", "-")
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(ini, fin))


def palabras(ruta):
    codigo = (
        "import json,sys\nfrom faster_whisper import WhisperModel\n"
        "m=WhisperModel('small',device='cpu',compute_type='int8')\n"
        f"s,_=m.transcribe(r'{ruta}',language='es',word_timestamps=True)\n"
        "print(json.dumps([[w.word.strip(),w.start,w.end,w.probability] for x in s for w in x.words]))")
    out = subprocess.run([WHISPER_PY, "-I", "-c", codigo], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    return json.loads(out.strip().splitlines()[-1])


def emocion(ruta):
    y, sr = librosa.load(str(ruta), sr=16000)
    f0, v, _ = librosa.pyin(y, fmin=60, fmax=300, sr=sr)
    f0 = f0[v & ~np.isnan(f0)]
    st = 12 * np.log2(f0 / np.median(f0))
    db = 20 * np.log10(librosa.feature.rms(y=y)[0] + 1e-9)
    db = db[db > db.max() - 35]
    return np.median(f0), st.std(), db.std()


lineas = []
pico, rms = nivel(crudo)
lineas.append(f"Nivel original: pico {pico:.1f} dB, promedio {rms:.1f} dB "
              f"({'BAJO: ideal pico entre -6 y -3' if pico < -9 else 'bien'})")
ps = pausas(crudo)
ruido = [nivel(crudo, a + 0.1, b - 0.1)[1] for a, b in ps if b - a > 0.5]
lineas.append("Ruido en las pausas: " + ", ".join(f"{r:.0f}" for r in ruido) + " dB")
lineas.append("Pausas de más de 0.35 s: " + ", ".join(f"{b - a:.1f}s@{a:.1f}" for a, b in ps))

ff("-y", "-i", str(crudo), "-af", "highpass=f=70,afftdn=nr=10:nf=-60,loudnorm=I=-18:TP=-1.5:LRA=11",
   "-ar", "48000", "-ac", "1", str(arreglada))

ws = palabras(arreglada)
lineas.append("Whisper: " + " ".join(w[0] for w in ws))
dudosas = [f"{w[0]} ({w[3]:.2f} @ {w[1]:.1f}s)" for w in ws if w[3] < 0.6]
lineas.append("Palabras dudosas: " + (", ".join(dudosas) or "ninguna"))

desde, hasta = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--tramo=")), "la:familia").split(":")
i0 = next((i for i, w in enumerate(ws) if w[0].lower().startswith(desde)), 0)
ini = ws[i0][1]
fin = next((w[2] for w in ws[i0:] if w[0].lower().strip(".,¿?").startswith(hasta)), None)
if fin:
    a, b = max(0, ini - 0.15), fin + 0.45
    ff("-y", "-i", str(arreglada), "-af",
       f"atrim={a}:{b},asetpts=N/SR/TB,afade=t=in:d=0.05,afade=t=out:st={b - a - 0.25}:d=0.2", str(tramo))
    tw = palabras(tramo)
    lineas.append(f"Tramo para clonar ({b - a:.1f} s): " + " ".join(w[0] for w in tw))
    lineas.append("  dudosas en el tramo: " + (", ".join(w[0] for w in tw if w[3] < 0.6) or "ninguna"))
    t0, tst, tdb = emocion(tramo)
    f0, fst, fdb = emocion(FISH3)
    lineas.append(f"Emoción del tramo: tono {t0:.0f} Hz, variación {tst:.1f} semitonos, volumen {tdb:.1f} dB "
                  f"(Fish 3: {f0:.0f} Hz, {fst:.1f} st, {fdb:.1f} dB)")
else:
    lineas.append(f"No encontré '{hasta}' en la transcripción: no recorté el tramo.")

reporte = "\n".join(lineas)
(CARPETA / f"{nombre}_reporte.txt").write_text(reporte, encoding="utf-8")
print(reporte)

if "--sin-telegram" not in sys.argv:
    for wav, etiqueta in [(arreglada, f"{nombre} arreglada"), (tramo, f"{nombre} tramo para clonar")]:
        if wav.exists():
            mp3 = wav.with_suffix(".mp3")
            ff("-y", "-loglevel", "error", "-i", str(wav), "-b:a", "160k", str(mp3))
            subprocess.run([BOT_PY, str(TELEGRAM), etiqueta, str(mp3)])
