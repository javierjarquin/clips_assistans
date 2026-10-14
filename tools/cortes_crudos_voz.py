"""Toma de voz de Javier -> reporte + cortes SIN MODIFICAR, por Telegram (11/10/2026).

Javier pidió que no se toque su voz: ni volumen ni limpieza ("las
modificaciones se escuchan fuerte"). Aquí solo se corta:
  A = de "Nadie" hasta "pozo"; B = hasta "Julio" (texto del rancho).
El volumen se sube solo en una copia temporal para que Whisper oiga mejor;
lo que se manda es el audio original recortado (con 10 ms de fundido para
que no truene el corte).

    .venv\\Scripts\\python.exe tools\\cortes_crudos_voz.py test9 [--sin-telegram]
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
ESPERADO = ("nadie escuchó nada esa noche pero a la mañana siguiente la puerta del rancho estaba "
            "abierta el perro ya no ladraba el coche rojo seguía ahí junto al pozo dónde estaba julio "
            "su hermana llamó a la policía a las seis y media tardaron tres horas en llegar y cuando "
            "llegaron ya era tarde hoy veintidós años después el expediente sigue cerrado y aquí el "
            "dato mata al gato").split()

nombre = sys.argv[1]
CARPETA.mkdir(parents=True, exist_ok=True)
crudo = CARPETA / f"{nombre}.wav"
crudo.write_bytes((ORIGEN / f"{nombre}.wav").read_bytes())


def ff(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stderr


def stats(ruta, a=None, b=None):
    filtro = (f"atrim={a}:{b}," if a is not None else "") + "astats=metadata=0"
    err = ff("-i", str(ruta), "-af", filtro, "-f", "null", "-")
    return (float(re.search(r"Peak level dB: (-?[\d.]+)", err).group(1)),
            float(re.search(r"RMS level dB: (-?[\d.]+)", err).group(1)))


def palabras(ruta):
    codigo = ("import json\nfrom faster_whisper import WhisperModel\n"
              "m=WhisperModel('small',device='cpu',compute_type='int8')\n"
              f"s,_=m.transcribe(r'{ruta}',language='es',word_timestamps=True)\n"
              "print(json.dumps([[w.word.strip(),w.start,w.end,w.probability] for x in s for w in x.words]))")
    out = subprocess.run([WHISPER_PY, "-I", "-c", codigo], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    return json.loads(out.strip().splitlines()[-1])


def limpia(p):
    return p.strip(" .,¿?¡!").lower()


pico, _ = stats(crudo)
ganancia = max(0.0, -3 - pico)
copia = CARPETA / f"_chk_{nombre}.wav"
ff("-y", "-loglevel", "error", "-i", str(crudo), "-af", f"volume={ganancia:.1f}dB", str(copia))
ws = palabras(copia)
dichas = [limpia(w[0]) for w in ws]

# Palabras del texto que no aparecen en lo que oyó Whisper (los números los
# escribe con cifra: no cuentan como error).
cifras = {"seis": "6", "veintidós": "22", "tres": "3"}
faltan = [p for p in ESPERADO if p not in dichas and cifras.get(p) not in dichas]
dudosas = [f"{w[0]} ({w[3]:.2f})" for w in ws if w[3] < 0.6]


def tiempo(prefijo, cual):
    return next(w[1 if cual == "ini" else 2] for w in ws if limpia(w[0]).startswith(prefijo))


siguiente = lambda t: next((w[1] for w in ws if w[1] > t), t + 0.6)  # noqa: E731
ini = max(0.0, tiempo("nadie", "ini") - 0.2)
cortes = {}
for letra, hasta in (("A", "pozo"), ("B", "juli")):
    fin_palabra = tiempo(hasta, "fin")
    fin = (fin_palabra + siguiente(fin_palabra)) / 2  # a mitad de la pausa
    destino = CARPETA / f"{nombre}_crudo_{letra}.wav"
    dur = fin - ini
    ff("-y", "-loglevel", "error", "-i", str(crudo), "-af",
       f"atrim={ini:.2f}:{fin:.2f},asetpts=N/SR/TB,afade=t=in:d=0.01,afade=t=out:st={dur - 0.01:.2f}:d=0.01",
       str(destino))
    chk = CARPETA / f"_chk_{nombre}_{letra}.wav"
    ff("-y", "-loglevel", "error", "-i", str(destino), "-af", f"volume={ganancia:.1f}dB", str(chk))
    cortes[letra] = (destino, dur, " ".join(w[0] for w in palabras(chk)))

y, sr = librosa.load(str(cortes["A"][0]), sr=16000)
f0, v, _ = librosa.pyin(y, fmin=60, fmax=300, sr=sr)
f0 = f0[v & ~np.isnan(f0)]
st = 12 * np.log2(f0 / np.median(f0))
db = 20 * np.log10(librosa.feature.rms(y=y)[0] + 1e-9)
db = db[db > db.max() - 35]
ruido = stats(crudo, 0.3, max(0.6, ini - 0.1))[1]

reporte = "\n".join([
    f"{nombre.upper()} (sin modificar, solo cortado)",
    f"- Volumen: pico {pico:.0f} dB ({'bajito' if pico < -15 else 'bien'})",
    f"- Ruido del cuarto: {ruido:.0f} dB ({'natural, sin supresion' if ruido > -72 else 'muy bajo: revisa si se prendio la supresion de ruido'})",
    f"- Emocion (corte A): tono {np.median(f0):.0f} Hz, varia {st.std():.1f} semitonos y {db.std():.1f} dB de volumen (Fish 3: 2.4 st, 6.4 dB)",
    "- Palabras del texto que Whisper no oyo: " + (", ".join(faltan) or "ninguna"),
    "- Palabras dudosas: " + (", ".join(dudosas) or "ninguna"),
    f"- Whisper oyo: {' '.join(w[0] for w in ws)}",
    f"A = {cortes['A'][1]:.1f} s: {cortes['A'][2]}",
    f"B = {cortes['B'][1]:.1f} s: {cortes['B'][2]}",
])
(CARPETA / f"{nombre}_reporte_crudo.txt").write_text(reporte, encoding="utf-8")
print(reporte)

if "--sin-telegram" not in sys.argv:
    subprocess.run([BOT_PY, str(TELEGRAM), reporte])
    for etiqueta, ruta in [(f"1 {nombre} ORIGINAL completa", crudo),
                           (f"A {nombre} cruda", cortes["A"][0]), (f"B {nombre} cruda", cortes["B"][0])]:
        for _ in range(3):
            if subprocess.run([BOT_PY, str(TELEGRAM), etiqueta, str(ruta)]).returncode == 0:
                break
