"""Prueba escrituras alternativas de palabras que la voz dice mal, y deja que
Whisper diga cuál se entiende. Voz de true crime (81f929e4) con num_step=32.

    .venv\\Scripts\\python.exe tools\\probar_pronunciaciones.py
"""

import sys
from pathlib import Path

import requests
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "pronunciacion"
SALIDA.mkdir(parents=True, exist_ok=True)

# (qué tiene que entenderse, [escrituras a probar])
PRUEBAS_1 = [
    ("jetta", ["detuvieron su Jetta blanco.", "detuvieron su Yeta blanco.",
               "detuvieron su Yéta blanco."]),
    ("tlalixcoyan", ["En el rancho El Limón, en Tlalixcoyan, había restos.",
                     "En el rancho El Limón, en Tlaliscóyan, había restos.",
                     "En el rancho El Limón, en Tlalis cóyan, había restos."]),
    ("mario", ["Iba con Bernardo Benítez, José Alfredo González, Mario Arturo Orozco y una "
               "adolescente de dieciséis años.",
               "Iba con Bernardo Benítez, José Alfredo González, con Mario Arturo Orozco y "
               "con una adolescente de dieciséis años."]),
]

# Segunda tanda (28/09/2026): Tlalixcoyan falló en las tres escrituras de
# arriba, y la lista de cuatro nombres se comió uno en cada intento.
PRUEBAS = [
    ("tlalix2", ["En el rancho El Limón, en el municipio de Tlalixcoyan, había restos.",
                 "En el rancho El Limón, en Tla-lis-có-yan, había restos.",
                 "En el rancho El Limón, en Tlalixcoyán, había restos.",
                 "En el rancho El Limón. En Tlalixcoyan. Había restos."]),
    ("lista2", ["Iba con Bernardo Benítez y José Alfredo González. También con Mario Arturo "
                "Orozco y una adolescente de dieciséis años."]),
]

modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
for clave, textos in PRUEBAS:
    for i, texto in enumerate(textos):
        wav = SALIDA / f"{clave}_{i}.wav"
        if not wav.exists():
            r = requests.post("http://localhost:3900/v1/audio/speech", timeout=1800, json={
                "model": "omnivoice", "voice": "81f929e4", "input": texto,
                "response_format": "wav", "num_step": 32})
            r.raise_for_status()
            wav.write_bytes(r.content)
        oido = " ".join(s.text.strip() for s in modelo.transcribe(str(wav), language="es")[0])
        print(f"{clave}_{i}: escrito {texto!r}\n        oído    {oido!r}", flush=True)
