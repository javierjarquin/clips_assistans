"""Manda por Telegram cada video del lote en cuanto aparece en la carpeta.

Espera a que el archivo deje de crecer (el archivado es una copia), lo baja a
720x1280 para entrar en el límite de 50 MB de un bot, y lo manda. Termina
cuando mandó `cantidad` videos o pasaron `horas` horas.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\vigilar_lote_telegram.py <carpeta> <cantidad> [horas]
"""

import subprocess
import sys
import time
from pathlib import Path

carpeta = Path(sys.argv[1])
cantidad = int(sys.argv[2])
limite = time.time() + float(sys.argv[3] if len(sys.argv) > 3 else 6) * 3600
enviar = Path(__file__).with_name("telegram_enviar.py")
mandados: set[str] = set()

while len(mandados) < cantidad and time.time() < limite:
    for mp4 in sorted(carpeta.glob("*.mp4")) if carpeta.exists() else []:
        if mp4.stem.endswith("_telegram") or mp4.name in mandados:
            continue
        tam = mp4.stat().st_size
        time.sleep(10)
        if mp4.stat().st_size != tam:
            continue  # todavía se está copiando
        liviano = mp4.with_name(f"{mp4.stem}_telegram.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", "scale=-2:1280",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "28", "-c:a", "aac",
                        "-b:a", "128k", "-movflags", "+faststart", str(liviano)], check=True)
        subprocess.run([sys.executable, str(enviar),
                        f"🎬 {mp4.stem} (Fish 3 v3, evidencia real). {len(mandados) + 1}/{cantidad}",
                        str(liviano)], check=False)
        mandados.add(mp4.name)
        print("mandado", mp4.name, flush=True)
    time.sleep(60)
print(f"fin: {len(mandados)} mandados", flush=True)
