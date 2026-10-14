"""Pasa el guion de Tierra Blanca al formato de evidencia que escribe Claude
(raíz "evidencia" + visual.evidencia por plano) para probar el pipeline real.
Incluye a propósito el enlace de la CNDH que da 404: se tiene que caer solo.

    .venv\\Scripts\\python.exe tools\\tierra_blanca_formato_evidencia.py
"""

import json
import shutil
from pathlib import Path

base = Path(r"C:\Android_in\guion-tierra-blanca-evidencia")
guion = json.loads((base / "guion.json").read_text(encoding="utf-8"))
M = "Milenio, cronología del caso"
guion["evidencia"] = [
    {"id": "e1", "tipo": "lugar", "wikimedia": "File:Central de autobuses en tierra blanca.jpg"},
    {"id": "e2", "tipo": "lugar", "wikimedia": "File:Mexico Veracruz Tierra Blanca location map.svg"},
    {"id": "e3", "tipo": "lugar", "wikimedia": "File:Palacio Municipal Tierra Blanca, Veracruz.jpg"},
    {"id": "e4", "tipo": "lugar", "wikimedia": "File:Iglesia en Tierra Blanca, Ver.jpg"},
    {"id": "e5", "tipo": "lugar", "buscar_wikimedia": "Glorieta Caritas Sonrientes Tierra Blanca"},
    {"id": "e6", "tipo": "persona", "wikimedia": "File:Javier Duarte de Ochoa.jpg"},
    {"id": "e7", "tipo": "documento", "pagina": 1, "fuente": "CNDH · Rec. 5VG/2017",
     "url": "https://www.cndh.org.mx/sites/default/files/doc/Recomendaciones/ViolacionesGraves/RecVG_005.pdf"},
    {"id": "e8", "tipo": "documento", "fuente": "CNDH · disculpa pública de Veracruz",
     "url": "https://hist.cndh.org.mx/documento/reconocimiento-de-responsabilidad-y-disculpa-publica-del-gobierno-del-estado-de-veracruz"},
    {"id": "e9", "tipo": "prensa", "fuente": "La Silla Rota, 12/01/2026",
     "url": "https://lasillarota.com/veracruz/estado/2026/1/12/ya-estamos-cansados-que-sentencien-responsables-jose-benitez-por-caso-tierra-blanca-490517.html"},
    {"id": "e10", "tipo": "prensa", "fuente": "Pie de Página",
     "url": "https://piedepagina.mx/tres-gobernadores-y-7-anos-sin-sentencias-por-jovenes-desaparecidos-en-tierra-blanca/"},
    {"id": "e11", "tipo": "documento", "fuente": "CNDH (enlace roto, prueba)",
     "url": "https://www.cndh.org.mx/documento/emite-cndh-recomendacion-por-violaciones-graves-derechos-humanos-al-gobierno-de-veracruz"},
    {"id": "f1", "tipo": "ficha", "titulo": "Detenidos el 11 de enero de 2016", "fuente": "Pie de Página",
     "renglones": ["José Benítez de la O", "Bernardo Benítez Arroniz", "José Alfredo González Díaz",
                   "Mario Arturo Orozco Sánchez", "Una joven de 16 años"]},
    {"id": "f2", "tipo": "ficha", "titulo": "11:37 · Tierra Blanca", "fuente": M,
     "renglones": ["Una cámara de seguridad cerca de un Chedraui graba a policías estatales "
                   "deteniendo un Jetta blanco."]},
    {"id": "f3", "tipo": "ficha", "titulo": "12:21 · En la camioneta", "fuente": M,
     "renglones": ["La cámara muestra a los jóvenes arriba de una camioneta de la policía.",
                   "21:00 · El Jetta aparece en Paso del Toro, Medellín, a más de 70 km."]},
    {"id": "f4", "tipo": "ficha", "titulo": "Detenidos, sin sentencia", "fuente": M,
     "renglones": ["14/01/2016 · Cuatro policías estatales. Aceptaron la detención; dijeron no "
                   "saber dónde estaban los jóvenes.",
                   "17/01/2016 · Marcos Conde Hernández, delegado de Seguridad Pública en "
                   "Tierra Blanca."]},
    {"id": "f5", "tipo": "ficha", "titulo": "20/01/2016 · El fiscal Luis Ángel Bravo", "fuente": M,
     "renglones": ["Un testigo afirmó que los policías entregaron a los jóvenes al crimen organizado."]},
    {"id": "f6", "tipo": "ficha", "titulo": "Rancho El Limón · Tlalixcoyan", "fuente": "Pie de Página",
     "renglones": ["Restos de unas 300 personas.", "Entre ellos, un fragmento de hueso de Bernardo Benítez."]},
    {"id": "f7", "tipo": "ficha", "titulo": "10 años · 20 detenidos · 0 sentencias",
     "fuente": "La Silla Rota, 12/01/2026",
     "renglones": ["Enero de 2016: cinco jóvenes de Playa Vicente detenidos por la Policía Estatal.",
                   "Enero de 2026: ninguna sentencia."]},
]
por_plano = {"p00": ["e9", "f7", "e10"], "p01": ["f1", "e2", "e1"],
             "p02": ["e1", "f2", "e4", "e5"], "p03": ["f3", "e5", "e4"], "p04": ["f4", "e3"],
             "p05": ["e6", "f5"], "p06": ["f6", "e7", "e8", "e11"], "p07": ["e9", "f7", "e10"]}
for p in guion["planos"]:
    if p["id"] in por_plano:
        p["visual"] = {"tipo": "archivo_historico", "evidencia": por_plano[p["id"]],
                       "descripcion": p["visual"].get("descripcion", ""),
                       "prompt_ia": "", "busqueda_medios": ""}
(base / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
for viejo in ("imagenes_manuales", "evidencia"):
    shutil.rmtree(base / viejo, ignore_errors=True)
print("guion en formato de evidencia:", len(guion["evidencia"]), "piezas")
