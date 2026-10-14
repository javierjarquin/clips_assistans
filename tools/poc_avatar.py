"""POC de avatar hablante con MuseTalk -- SUELTO, fuera del pipeline.

Toma una placa (video corto de una cara) y un audio ya generado, y devuelve
un video con la boca sincronizada a ese audio. NO integra nada al pipeline:
es solo para medir si el resultado y los tiempos justifican seguir.

    python tools/poc_avatar.py --placa placa.mp4 --audio narracion.wav --out salida.mp4

Por que MuseTalk y no HeyGem: HeyGem exige NVIDIA/CUDA y esta maquina tiene
una Radeon, sin fallback por CPU. MuseTalk es MIT (codigo y pesos, uso
comercial permitido) y su seleccion de dispositivo cae sola a CPU.

Por que MuseTalk y no Wav2Lip: los pesos de Wav2Lip vienen de LRS2, que es
licencia NO comercial.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

MUSETALK_DIR = Path(__file__).resolve().parent / "MuseTalk"
MUSETALK_PY = MUSETALK_DIR / ".venv" / "Scripts" / "python.exe"

# MuseTalk fue entrenado a 25fps; con otro fps la boca se desfasa del audio.
FPS_ESPERADO = 25


class PocError(RuntimeError):
    """Fallo de la POC, con mensaje accionable."""


def _log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def _validar_entradas(placa: Path, audio: Path) -> None:
    """Todo lo que puede faltar, antes de cargar 3.6 GB de modelo."""
    if not MUSETALK_DIR.exists():
        raise PocError(f"No existe MuseTalk en {MUSETALK_DIR}. Cloná el repo primero.")
    if not MUSETALK_PY.exists():
        raise PocError(f"No existe el intérprete de MuseTalk en {MUSETALK_PY}.")

    unet = MUSETALK_DIR / "models" / "musetalkV15" / "unet.pth"
    if not unet.exists():
        raise PocError(
            f"Faltan los pesos ({unet}). Corré download_weights.sh o bajalos a mano."
        )

    if not placa.exists():
        raise PocError(f"No existe la placa: {placa}")
    if not audio.exists():
        raise PocError(f"No existe el audio: {audio}")

    fps = _fps(placa)
    if fps is not None and abs(fps - FPS_ESPERADO) > 0.5:
        # Aviso, no error: MuseTalk igual corre, pero la sincronía sufre.
        _log(
            f"AVISO: la placa está a {fps:.2f} fps y MuseTalk espera {FPS_ESPERADO}. "
            "Convertila con: ffmpeg -i placa.mp4 -r 25 placa_25.mp4"
        )


def _fps(video: Path) -> float | None:
    try:
        salida = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate",
             "-of", "default=nw=1:nk=1", str(video)],
            capture_output=True, text=True, timeout=60,
        ).stdout.strip()
        num, den = salida.split("/")
        return float(num) / float(den)
    except Exception:  # noqa: BLE001 -- es un chequeo informativo, no bloquea
        return None


def _duracion(ruta: Path) -> float | None:
    try:
        return float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(ruta)],
            capture_output=True, text=True, timeout=60,
        ).stdout.strip())
    except Exception:  # noqa: BLE001
        return None


def generar(placa: Path, audio: Path, destino: Path, batch_size: int = 4,
            dispositivo: str = "", fp16: bool = False) -> float:
    """Corre MuseTalk. Devuelve los segundos que tardó."""
    # Absolutas SIEMPRE: inference.py corre con cwd=MUSETALK_DIR, así que una
    # ruta relativa del usuario no resuelve ahí. Cuando pasó, MuseTalk no
    # fallaba al abrir el archivo -- seguía y moría después con un opaco
    # "cannot unpack non-iterable NoneType object".
    placa = placa.resolve()
    audio = audio.resolve()
    destino = destino.resolve()

    _validar_entradas(placa, audio)

    dur_audio = _duracion(audio)
    _log(f"placa : {placa}  ({_duracion(placa) or '?'}s)")
    _log(f"audio : {audio}  ({dur_audio or '?'}s)")

    # Carpeta de trabajo PERSISTENTE, no temporal: la extracción de landmarks
    # tardó ~18 min sobre 377 fotogramas a 1080x1920, y con --use_saved_coord
    # se reutiliza en corridas siguientes en vez de rehacerla.
    trabajo = destino.parent / "_trabajo_musetalk"
    trabajo.mkdir(parents=True, exist_ok=True)
    config = trabajo / "poc.yaml"
    config.write_text(
        "poc:\n"
        f"  video_path: {placa.as_posix()}\n"
        f"  audio_path: {audio.as_posix()}\n",
        encoding="utf-8",
    )
    resultados = trabajo / "resultados"

    args = [
        str(MUSETALK_PY), "-m", "scripts.inference",
        "--inference_config", str(config),
        "--result_dir", str(resultados),
        "--unet_model_path", "./models/musetalkV15/unet.pth",
        "--unet_config", "./models/musetalkV15/musetalk.json",
        "--version", "v15",
        "--fps", str(FPS_ESPERADO),
        "--batch_size", str(batch_size),
        "--ffmpeg_path", "ffmpeg",
        "--saved_coord",
    ]
    # La Radeon tiene 8 GB, pero el UNet en float32 se lleva 3.4 y cualquier
    # juego abierto se lleva el resto: con Gears 5 corriendo (3.9 GB) la
    # inferencia murio con "not enough GPU video memory" pidiendo 128 MB. En
    # float16 el modelo baja a ~1.7 GB y sobrevive a que la placa este ocupada.
    # Ojo: Win32_VideoController.AdapterRAM informa 4 GB por un campo de 32
    # bits que satura; el valor real esta en el registro, qwMemorySize.
    if fp16:
        args.append("--use_float16")
    # MuseTalk nombra el .pkl segun la placa y lo deja junto al result_dir, no
    # dentro. Se busca por nombre a proposito: reusar coords de OTRA placa (o
    # de la misma a otra resolucion) daria recortes fuera de lugar.
    if any(trabajo.rglob(f"{placa.stem}.pkl")):
        args.append("--use_saved_coord")
        _log(f"reusando landmarks ya calculados de {placa.stem}")

    # MuseTalk imprime mensajes con caracteres CJK. Sin esto, la consola de
    # Windows (cp1252) no puede codificarlos y el proceso MUERE por un print,
    # después de 18 minutos de trabajo ya hecho.
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    if dispositivo:
        # La eleccion de dispositivo la lee scripts/inference.py (parcheado):
        # "dml" manda UNet/VAE/whisper a la Radeon via DirectML.
        entorno["MUSETALK_DEVICE"] = dispositivo

    _log("arrancando MuseTalk (la primera vez carga ~3.6 GB de modelo)...")
    inicio = time.time()
    proc = subprocess.run(args, cwd=str(MUSETALK_DIR), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=entorno)
    transcurrido = time.time() - inicio

    if proc.returncode != 0:
        cola = (proc.stderr or proc.stdout or "")[-2500:]
        raise PocError(
            f"MuseTalk falló (código {proc.returncode}) tras {transcurrido:.0f}s.\n\n{cola}"
        )

    # Por nombre, no "el ultimo alfabetico": el result_dir es persistente y
    # acumula corridas anteriores. MuseTalk nombra la salida
    # <placa>_<audio>.mp4, y ordenar alfabeticamente devolvia el mp4 de OTRA
    # corrida (visto en real: una corrida de 120s reporto 15s de duracion).
    #
    # Y solo lo de ESTA corrida: MuseTalk puede salir con codigo 0 despues de
    # imprimir "Error occurred during processing" sin escribir nada (visto en
    # real: se quedo sin memoria de GPU). Sin el filtro por fecha se copiaba el
    # mp4 viejo y se reportaba exito.
    generados = sorted(
        (f for f in resultados.rglob(f"{placa.stem}_{audio.stem}.mp4")
         if f.stat().st_mtime >= inicio),
        key=lambda f: f.stat().st_mtime,
    )
    if not generados:
        raise PocError(
            f"MuseTalk no dejo un .mp4 nuevo en {resultados} tras {transcurrido:.0f}s.\n"
            f"Ultimas lineas:\n{(proc.stdout or '')[-1500:]}"
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(generados[-1], destino)

    return transcurrido


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--placa", required=True, type=Path, help="video corto de la cara")
    ap.add_argument("--audio", required=True, type=Path, help="audio a sincronizar")
    ap.add_argument("--out", required=True, type=Path, help="mp4 de salida")
    ap.add_argument("--fp16", action="store_true",
                    help="media precision: obligatorio en la Radeon de 4 GB")
    ap.add_argument("--batch-size", type=int, default=4,
                    help="bajalo si se queda sin memoria (def. 4)")
    ap.add_argument("--dispositivo", default="", choices=["", "dml"],
                    help="dml = GPU Radeon via DirectML; vacio = CPU")
    args = ap.parse_args()

    _log("=== POC avatar (MuseTalk) ===")
    try:
        transcurrido = generar(args.placa, args.audio, args.out, args.batch_size,
                               args.dispositivo, args.fp16)
    except PocError as exc:
        _log("FALLÓ")
        print(f"\n{exc}", file=sys.stderr)
        return 1

    dur_audio = _duracion(args.audio) or 0
    dur_salida = _duracion(args.out)
    _log(f"LISTO en {transcurrido:.0f}s ({transcurrido/60:.1f} min)")
    print()
    print(f"  salida        : {args.out}")
    print(f"  duración      : {dur_salida}s")
    if dur_audio:
        # El número que decide si esto es viable en lotes nocturnos.
        print(f"  factor        : {transcurrido/dur_audio:.1f}x tiempo real")
        print(f"  proyección    : un video de 130s tardaría "
              f"{130*(transcurrido/dur_audio)/60:.0f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
