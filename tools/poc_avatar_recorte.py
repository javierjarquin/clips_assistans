"""Quita el fondo del clip del avatar -- SUELTO, fuera del pipeline.

Genera una MASCARA en blanco y negro (una por fotograma) con el segmentador
de personas de MediaPipe. La mascara se guarda como video sin perdida y luego
`poc_avatar_overlay.py --mascara` la usa con `alphamerge` para pegar solo a la
persona, sin el cuarto de fondo.

    python tools/poc_avatar_recorte.py --avatar avatar.mp4 --out mascara.mkv

Va aparte del overlay a proposito: la mascara depende solo de la placa, asi
que se calcula una vez y se reusa aunque cambien el encuadre, la esquina o el
tamano del avatar.

Por que MediaPipe y no rembg/MODNet: el modelo SelfieSegmenter es Apache-2.0
(uso comercial explicito, mismo criterio que descarto Wav2Lip) y corre en CPU
a milisegundos por fotograma. rembg/u2net tarda ~1.5 s por fotograma y MODNet
publica sus pesos como no comercial.
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

MODELO = Path(__file__).resolve().parent / "modelos" / "selfie_segmenter.tflite"


class RecorteError(RuntimeError):
    pass


def _log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def _segmentador():
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    if not MODELO.exists():
        raise RecorteError(
            f"Falta el modelo {MODELO}. Bajalo con:\n"
            "  curl -sSL -o tools/modelos/selfie_segmenter.tflite "
            "https://storage.googleapis.com/mediapipe-models/image_segmenter/"
            "selfie_segmenter/float16/latest/selfie_segmenter.tflite"
        )
    opciones = vision.ImageSegmenterOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODELO)),
        running_mode=vision.RunningMode.VIDEO,
        output_confidence_masks=True,
    )
    return vision.ImageSegmenter.create_from_options(opciones)


def _mascara_de(resultado, alto: int, ancho: int) -> np.ndarray:
    """Confianza de 'persona' en 0..255, del resultado de MediaPipe."""
    masks = resultado.confidence_masks
    if not masks:
        raise RecorteError("MediaPipe no devolvio ninguna mascara de confianza")
    # SelfieSegmenter devuelve 2 categorias (fondo, persona) o 1 sola con la
    # confianza de primer plano. Se toma la ultima en ambos casos.
    m = masks[-1].numpy_view()
    if m.shape[:2] != (alto, ancho):
        m = cv2.resize(m, (ancho, alto), interpolation=cv2.INTER_LINEAR)
    return np.clip(m * 255.0, 0, 255).astype(np.uint8)


def _suavizar(mask: np.ndarray, encoger: int, desenfoque: int) -> np.ndarray:
    # Encoger un pelo antes de desenfocar: sin esto queda un halo del color de
    # la pared alrededor de la silueta, muy visible sobre fondos oscuros.
    if encoger > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (encoger * 2 + 1,) * 2)
        mask = cv2.erode(mask, k)
    if desenfoque > 0:
        lado = desenfoque * 2 + 1
        mask = cv2.GaussianBlur(mask, (lado, lado), 0)
    return mask


def generar(
    avatar: Path,
    destino: Path,
    encoger: int = 2,
    desenfoque: int = 3,
    limite: int | None = None,
) -> float:
    avatar = avatar.resolve()
    destino = destino.resolve()
    if not avatar.exists():
        raise RecorteError(f"No existe el avatar: {avatar}")

    cap = cv2.VideoCapture(str(avatar))
    if not cap.isOpened():
        raise RecorteError(f"No pude abrir {avatar}")
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    _log(f"avatar : {ancho}x{alto} @ {fps:.2f}fps, {total} fotogramas")

    destino.parent.mkdir(parents=True, exist_ok=True)
    # ffv1 sin perdida: un mp4 con perdida deja halos de bloque en el borde de
    # la silueta, que sobre la imagen de fondo se ven como un contorno sucio.
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{ancho}x{alto}",
         "-r", f"{fps}", "-i", "-",
         "-c:v", "ffv1", "-pix_fmt", "gray", str(destino)],
        stdin=subprocess.PIPE,
    )

    import mediapipe as mp

    inicio = time.time()
    n = 0
    try:
        with _segmentador() as seg:
            while True:
                ok, frame = cap.read()
                if not ok or (limite is not None and n >= limite):
                    break
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                # Timestamp en ms derivado del indice: los de OpenCV a veces
                # se repiten y MediaPipe exige que sean estrictamente crecientes.
                res = seg.segment_for_video(imagen, int(n * 1000 / fps))
                mask = _mascara_de(res, alto, ancho)
                mask = _suavizar(mask, encoger, desenfoque)
                ffmpeg.stdin.write(mask.tobytes())
                n += 1
                if total and n % 500 == 0:
                    _log(f"  {n}/{total} fotogramas")
    finally:
        cap.release()
        if ffmpeg.stdin:
            ffmpeg.stdin.close()
        ffmpeg.wait()

    if ffmpeg.returncode != 0:
        raise RecorteError(f"ffmpeg fallo al escribir la mascara (codigo {ffmpeg.returncode})")
    if n == 0:
        raise RecorteError(f"No pude leer ningun fotograma de {avatar}")

    _log(f"mascara: {n} fotogramas -> {destino}")
    return time.time() - inicio


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--avatar", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="mascara .mkv")
    ap.add_argument("--encoger", type=int, default=2, help="pixeles de erosion (def. 2)")
    ap.add_argument("--desenfoque", type=int, default=3, help="suavizado del borde (def. 3)")
    ap.add_argument("--limite", type=int, help="solo los primeros N fotogramas (para probar)")
    args = ap.parse_args()

    try:
        t = generar(args.avatar, args.out, args.encoger, args.desenfoque, args.limite)
    except RecorteError as exc:
        _log("FALLO")
        print(f"\n{exc}", file=sys.stderr)
        return 1

    _log(f"LISTO en {t:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
