"""Rearma un true crime ya narrado con la config actual del bot (logo fijo,
sin gato) para verlo en un render real. No vuelve a sintetizar la voz.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\rearmar_con_logo.py <slug>
"""

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BOT = Path(r"C:\dato-mata-gato-bot")
sys.path.insert(0, str(BOT / "src"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BOT / ".env")

from dato_mata_gato_bot import pipeline  # noqa: E402

slug = sys.argv[1]
print("voz de true crime:", pipeline.voz_de_true_crime(slug), flush=True)
ok, out = pipeline._run_narrator_generate(slug)
print("ok" if ok else out[-2000:], flush=True)
final = pipeline.NARRATOR_PROJECTS / slug / "final.mp4"
if ok:
    for t in (3, 30):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(final),
                        "-frames:v", "1", "-vf", "scale=360:-2",
                        str(Path(__file__).resolve().parents[1] / "analisis" / f"_logo_{t}s.jpg")])
