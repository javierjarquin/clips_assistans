"""Agrega al guion de Aguakan el bloqueo de Urbi del 3 de octubre de 2026 y
arma su evidencia (sin Claude).

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\aguakan_agregar_urbi.py
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, r"C:\dato-mata-gato-bot\src")
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.WARNING)

from dato_mata_gato_bot import evidencia, revision_guion  # noqa: E402

ruta = Path(r"C:\Android_in\guion-aguakan-cancun\guion.json")
g = json.loads(ruta.read_text(encoding="utf-8-sig"))
URL = "https://grupoanimal.mx/quintana-roo/sociedad/lluvias-cancun-dejan-inundaciones-socavones-protestas"
g["_schema"]["fuentes"]["urbi"] = (
    f"{URL} (04/10/2026: la noche del sábado, vecinos de Urbi bloquean la avenida López "
    "Portillo; baja presión desde días antes de la tormenta y sin agua tras las lluvias; "
    "piden al Ayuntamiento de Benito Juárez presionar a Aguakan)")
ids = {p["id"] for p in g["evidencia"]}
if "e9" not in ids:
    g["evidencia"] += [
        {"id": "e9", "tipo": "documento", "fuente": "Grupo Animal, 04/10/2026", "url": URL},
        {"id": "f5", "tipo": "ficha", "titulo": "Sábado 3 de octubre de 2026 · Urbi",
         "fuente": "Grupo Animal, 04/10/2026",
         "renglones": ["Vecinos bloquean la avenida López Portillo",
                       "Días con baja presión; sin agua tras las lluvias",
                       "Piden al Ayuntamiento presionar a Aguakan"]},
    ]
for pl in g["planos"]:
    if pl["id"] == "p06":
        pl["narracion"] = ("Y este sábado, vecinos de Urbi bloquearon la avenida López Portillo: "
                           "llevaban días sin agua. En agosto, Kusamil y Paraíso Maya pasaron "
                           "semanas igual.")
        pl["visual"]["evidencia"] = ["f5", "e9", "e4"]
        pl["texto_en_pantalla"] = "URBI SIN AGUA · 3 DE OCTUBRE"
ruta.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")

print("problemas:", revision_guion.problemas(g))
print("palabras:", sum(len(p["narracion"].split()) for p in g["planos"]))
rep = evidencia.preparar("guion-aguakan-cancun")
print(rep.resumen(), rep.fallidas)
m = json.loads((ruta.parent / "evidencia" / "manifest.json").read_text(encoding="utf-8-sig"))
print("e9 |", m.get("e9", {}).get("titular"))
