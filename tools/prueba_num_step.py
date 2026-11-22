"""Prueba a ciegas: ¿se nota la voz con 16 pasos en vez de 32? (22/11/2026)

La voz es lo más lento de un video (VoiceStudio/OmniVoice en CPU, ~13x el
largo del audio con num_step=32, según pipeline.py). El README de OmniVoice
sugiere num_step=16 "for faster inference", a cambio de algo de calidad. Esto
genera el MISMO texto con 16 y con 32 (misma voz, misma semilla) para 3 guiones
reales, mide cuánto tardó cada uno y los guarda como A y B al azar:

    analisis/prueba_num_step/<n>_A.wav, <n>_B.wav   para escuchar
    analisis/prueba_num_step/votos.csv               Javier anota cuál prefiere
    analisis/prueba_num_step/clave.json              cuál es cuál y los tiempos (no abrir antes de votar)

    python tools/prueba_num_step.py [slug ...]     (sin slugs: los 3 guiones más nuevos con voz viral)
    python tools/prueba_num_step.py resultado      cruza votos.csv con la clave

Correrlo con la fábrica sin renderizar: VoiceStudio atiende un pedido a la vez y
los tiempos saldrían inflados.
"""

import csv
import json
import random
import sys
import time
import wave
from pathlib import Path

import requests

ANDROID_IN = Path(r"C:\Android_in")
BOT_ENV = Path(r"C:\dato-mata-gato-bot\.env")
TTS_KOKORO_SRC = r"C:\tts-kokoro\src"
VOICESTUDIO = "http://localhost:3900/v1/audio/speech"
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "prueba_num_step"
PERFILES = {"viral_a": "VOICESTUDIO_VOICE_ID_VIRAL_A", "viral_b": "VOICESTUDIO_VOICE_ID_VIRAL_B",
            "viral_c": "VOICESTUDIO_VOICE_ID_VIRAL_C", "fish3": "VOICESTUDIO_VOICE_ID_CRIMEN"}
PASOS = (16, 32)
PLANOS = 2   # cuántos planos de cada guion (~20-30 s de voz)


def del_env(clave: str) -> str:
    for linea in BOT_ENV.read_text(encoding="utf-8", errors="replace").splitlines():
        nombre, sep, resto = linea.strip().partition("=")
        if sep and not nombre.startswith("#") and nombre.strip() == clave:
            return resto.split("#")[0].strip()
    return ""


def guiones(n: int = 3) -> list[str]:
    """Los guiones más nuevos de Dato Mata Gato con planos y voz viral."""
    salida = []
    for carpeta in sorted(ANDROID_IN.glob("guion-*"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            g = json.loads((carpeta / "guion.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(g, dict) and g.get("planos") and g.get("voz_narrador") in PERFILES:
            salida.append(carpeta.name)
        if len(salida) == n:
            break
    return salida


def texto_de(slug: str) -> tuple[str, str]:
    sys.path.insert(0, TTS_KOKORO_SRC)
    from tts_kokoro.domain.text_normalizer import normalize_text

    g = json.loads((ANDROID_IN / slug / "guion.json").read_text(encoding="utf-8"))
    planos = g["planos"][1:1 + PLANOS]   # p00 suele ser muy corto
    return " ".join(normalize_text(p["narracion"]) for p in planos), g["voz_narrador"]


def generar(texto: str, voz: str, pasos: int, destino: Path) -> float:
    cuerpo = {"model": "omnivoice", "voice": voz, "response_format": "wav", "language": "es",
              "num_step": pasos, "seed": 1234, "input": texto}
    inicio = time.time()
    for _ in range(40):
        r = requests.post(VOICESTUDIO, timeout=1800, json=cuerpo)
        if r.status_code != 429:
            break
        time.sleep(30)
    r.raise_for_status()
    destino.write_bytes(r.content)
    return time.time() - inicio


def duracion(wav: Path) -> float:
    with wave.open(str(wav)) as w:
        return w.getnframes() / w.getframerate()


def correr(slugs: list[str]) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    clave = {}
    for n, slug in enumerate(slugs, 1):
        texto, nombre_voz = texto_de(slug)
        voz = del_env(PERFILES[nombre_voz])
        letras = ["A", "B"]
        random.shuffle(letras)
        clave[str(n)] = {"slug": slug, "voz": nombre_voz, "texto": texto}
        for pasos, letra in zip(PASOS, letras):
            wav = SALIDA / f"{n}_{letra}.wav"
            seg = generar(texto, voz, pasos, wav)
            dur = duracion(wav)
            clave[str(n)][letra] = {"num_step": pasos, "segundos_generando": round(seg, 1),
                                    "segundos_de_audio": round(dur, 1), "veces_tiempo_real": round(seg / dur, 1)}
            print(f"{n} {letra}: {pasos} pasos, {seg:.0f} s para {dur:.1f} s de audio ({seg / dur:.1f}x)",
                  flush=True)
    (SALIDA / "clave.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1), encoding="utf-8")
    votos = SALIDA / "votos.csv"
    if not votos.exists():
        with votos.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["n", "prefiero (A, B o igual)", "notas"])
            for n in clave:
                w.writerow([n, "", ""])
    print(f"\nListo: escucha {SALIDA}\\<n>_A.wav y _B.wav y anota en votos.csv. No abras clave.json antes.")


def resultado() -> None:
    clave = json.loads((SALIDA / "clave.json").read_text(encoding="utf-8"))
    with (SALIDA / "votos.csv").open(encoding="utf-8-sig") as f:
        filas = list(csv.reader(f))[1:]
    conteo = {16: 0, 32: 0, "igual": 0}
    for n, voto, *_ in filas:
        voto = voto.strip().upper()
        if voto in ("A", "B"):
            conteo[clave[n][voto]["num_step"]] += 1
        elif voto:
            conteo["igual"] += 1
    rapidez = {p: [v["veces_tiempo_real"] for c in clave.values() for k, v in c.items()
                   if isinstance(v, dict) and v.get("num_step") == p] for p in PASOS}
    print(f"Preferencias: 16 pasos {conteo[16]}, 32 pasos {conteo[32]}, igual {conteo['igual']}")
    for p, xs in rapidez.items():
        print(f"{p} pasos: {sum(xs) / len(xs):.1f}x tiempo real (promedio de {len(xs)})")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.argv[1:] == ["resultado"]:
        resultado()
    else:
        correr(sys.argv[1:] or guiones())
