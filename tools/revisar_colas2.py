"""Segunda mirada a las colas: la cola SOLA (con silencio alrededor), y la
comparación contra la voz anterior del canal, que no tenía la queja del "cia".

    .venv\\Scripts\\python.exe tools\\revisar_colas2.py <slug_fish3> <slug_voz_vieja>
"""

import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
salida = Path(__file__).resolve().parents[1] / "analisis" / "colas"


def colas(slug: str, transcribir: bool) -> list[float]:
    rmss = []
    for wav in sorted((Path(r"C:\tts-kokoro\projects") / slug / "narracion").glob("p*.wav")):
        audio, sr = sf.read(wav, dtype="float32")
        palabras = [w for s in modelo.transcribe(str(wav), language="es", word_timestamps=True,
                                                 vad_filter=False)[0] for w in s.words]
        if not palabras:
            continue
        fin = palabras[-1].end
        cola = audio[int(fin * sr):]
        rms = float(np.sqrt(np.mean(cola ** 2))) if len(cola) else 0.0
        rmss.append(rms)
        if transcribir and len(cola) > sr * 0.1:
            pad = np.zeros(int(sr * 0.5), dtype="float32")
            ruta = salida / f"{slug}_{wav.stem}_solo_cola.wav"
            sf.write(ruta, np.concatenate([pad, cola, pad]), sr)
            oido = " ".join(s.text.strip() for s in modelo.transcribe(
                str(ruta), language="es", vad_filter=False, no_speech_threshold=0.95)[0])
            print(f"  {slug} {wav.stem}: cola {len(cola) / sr:.2f}s rms {rms:.3f} -> {oido!r}",
                  flush=True)
    return rmss


salida.mkdir(parents=True, exist_ok=True)
fish, vieja = sys.argv[1], sys.argv[2]
r_fish = colas(fish, True)
r_vieja = colas(vieja, False)
print(f"\nrms medio de la cola: Fish 3 {np.mean(r_fish):.3f}  |  voz anterior {np.mean(r_vieja):.3f}")
