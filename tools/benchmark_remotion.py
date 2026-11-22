"""¿Cuántas pestañas en paralelo le convienen al render de Remotion? (22/11/2026)

La docs de Remotion (remotion.dev/docs/terminology/concurrency) dice que el
default (la mitad de los núcleos) no siempre es el mejor, y que de más y de
menos frenan igual: hay que medirlo en la máquina. Esto renderiza los MISMOS
cuadros de dos videos reales con varias concurrencias y mide cuánto tarda:

  - Dato Mata Gato: poc_remotion, composición CapituloPlus (render_plus.py --solo-props)
  - tradiciones/papasia: tradiciones_3d, composición Tradicion (render.py; la voz sale de su caché)

    python tools/benchmark_remotion.py [--plus <slug>] [--tres-d <slug>] [--valores 4,8,12,16,24] [--cuadros 600]

Resultado en analisis/remotion_concurrencia/resultado.csv. Correrlo con la
fábrica sin renderizar ni generar voz, o los tiempos no sirven.
"""

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

NARRADOR = Path(r"C:\illustrated-narrator")
PYTHON_NARRADOR = NARRADOR / ".venv" / "Scripts" / "python.exe"
POC = NARRADOR / "poc_remotion"
TRES_D = NARRADOR / "tradiciones_3d"
SALIDA = Path(__file__).resolve().parents[1] / "analisis" / "remotion_concurrencia"


def preparar_plus(slug: str) -> Path:
    subprocess.run([str(PYTHON_NARRADOR), "scripts/render_plus.py", slug, "--solo-props"], cwd=POC, check=True)
    return POC / "public" / slug / "props.json"


def preparar_3d(slug: str) -> Path:
    # render.py hace voz (caché), Whisper, props y el render completo; el render
    # de 75 s tarda ~1 min, así que de paso sirve de calentamiento.
    subprocess.run([str(PYTHON_NARRADOR), "scripts/render.py", slug], cwd=TRES_D, check=True)
    return TRES_D / "public" / slug / "props.json"


def renderizar(carpeta: Path, composicion: str, props: Path, cuadros: int, concurrencia: str, destino: Path) -> float:
    entorno = {**os.environ, "REMOTION_CONCURRENCY": concurrencia}
    if not concurrencia:
        entorno.pop("REMOTION_CONCURRENCY")
    inicio = time.time()
    subprocess.run(["npx", "remotion", "render", "src/index.ts", composicion, str(destino), f"--props={props}",
                    "--codec=h264", "--crf=20", "--timeout=120000", "--gl=angle", f"--frames=0-{cuadros - 1}"],
                   cwd=carpeta, env=entorno, check=True, shell=(sys.platform == "win32"),
                   stdout=subprocess.DEVNULL)
    return time.time() - inicio


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plus", default="guion-viral-fumigacion-mariposas-monterrey")
    ap.add_argument("--tres-d", default="guion-tradicion-corona-navidena")
    ap.add_argument("--valores", default=",4,8,12,16,24", help="vacío = default de Remotion")
    ap.add_argument("--cuadros", type=int, default=600)
    a = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)
    nuevos = [d for d in (POC / "public" / a.plus, TRES_D / "public" / a.tres_d) if not d.exists()]
    casos = [("plus", POC, "CapituloPlus", preparar_plus(a.plus)),
             ("3d", TRES_D, "Tradicion", preparar_3d(a.tres_d))]
    filas = []
    try:
        for nombre, carpeta, comp, props in casos:
            for valor in a.valores.split(","):
                seg = renderizar(carpeta, comp, props, a.cuadros, valor, SALIDA / f"{nombre}_{valor or 'default'}.mp4")
                filas.append({"render": nombre, "concurrencia": valor or "default", "cuadros": a.cuadros,
                              "segundos": round(seg, 1), "cuadros_por_segundo": round(a.cuadros / seg, 1)})
                print(f"{nombre} concurrencia={valor or 'default'}: {seg:.0f} s ({a.cuadros / seg:.1f} cuadros/s)",
                      flush=True)
    finally:
        for d in nuevos:   # public/<slug> lo borra el bot al terminar; aquí igual
            shutil.rmtree(d, ignore_errors=True)
        for mp4 in SALIDA.glob("*.mp4"):
            mp4.unlink()
        with (SALIDA / "resultado.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["render", "concurrencia", "cuadros", "segundos", "cuadros_por_segundo"])
            w.writeheader()
            w.writerows(filas)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
