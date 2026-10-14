"""Borra piezas de evidencia de un guion y las vuelve a armar.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\rehacer_piezas.py <slug> e1 e2 ...
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, r"C:\dato-mata-gato-bot\src")
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.WARNING)

from dato_mata_gato_bot import evidencia  # noqa: E402

slug, ids = sys.argv[1], sys.argv[2:]
carpeta = Path(r"C:\Android_in") / slug / "evidencia"
manifest = json.loads((carpeta / "manifest.json").read_text(encoding="utf-8-sig"))
for pid in ids:
    manifest.pop(pid, None)
    (carpeta / f"{pid}.jpg").unlink(missing_ok=True)
(carpeta / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
rep = evidencia.preparar(slug)
print(rep.resumen(), rep.fallidas)
m = json.loads((carpeta / "manifest.json").read_text(encoding="utf-8-sig"))
for pid in ids:
    print(pid, "|", m.get(pid, {}).get("titular"))
