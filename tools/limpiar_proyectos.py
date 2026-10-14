"""Libera disco borrando los intermedios de los proyectos del narrador.

    python tools/limpiar_proyectos.py                 # simulacro, no borra nada
    python tools/limpiar_proyectos.py --borrar        # borra de verdad
    python tools/limpiar_proyectos.py --borrar --dias 3   # deja los recientes

Borra `media/`, `images/` y `clips/`, que son el 90% del peso y se pueden
regenerar. NUNCA toca ningún `final*.mp4`: medido el 19/09/2026, los 137
videos pesaban 15.5 GB de 183 -- el problema nunca fueron los videos.

Eso importa porque los videos NO están todos respaldados afuera: los de lote
grande se COPIAN a `Android_in/lotes/`, los de lote normal van a Drive, y
entre 20 y 50 existían únicamente dentro de su proyecto. Borrar carpetas
enteras de proyecto sí perdería material.

El costo de borrar los medios: regenerar un video viejo vuelve a investigar y
bajar stock, y puede elegir imágenes distintas a las del original. Para los ya
publicados da igual; para rehacer uno idéntico, no.
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

PROYECTOS = Path(r"C:\illustrated-narrator\projects")
BORRABLES = ("media", "images", "clips")


def _peso(ruta: Path) -> int:
    total = 0
    for p in ruta.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def _videos(base: Path) -> list[Path]:
    """Todos los final*.mp4 y respaldos. Se cuentan antes y después para
    demostrar que la limpieza no se llevó ninguno."""
    return sorted(
        p for p in base.glob("*/*.mp4")
        if p.name.startswith(("final", "_respaldo"))
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--borrar", action="store_true",
                    help="sin esto solo informa, no toca nada")
    ap.add_argument("--dias", type=float, default=0,
                    help="conservar los proyectos tocados en los últimos N días")
    ap.add_argument("--raiz", type=Path, default=PROYECTOS)
    args = ap.parse_args()

    if not args.raiz.exists():
        print(f"No existe {args.raiz}")
        return 1

    antes = _videos(args.raiz)
    print(f"videos antes de empezar: {len(antes)}")

    ahora = time.time()
    objetivos: list[tuple[Path, int]] = []
    conservados = 0
    for proyecto in sorted(args.raiz.iterdir()):
        if not proyecto.is_dir():
            continue
        if args.dias and (ahora - proyecto.stat().st_mtime) / 86400 <= args.dias:
            conservados += 1
            continue
        for nombre in BORRABLES:
            carpeta = proyecto / nombre
            if carpeta.is_dir():
                objetivos.append((carpeta, _peso(carpeta)))

    total = sum(p for _, p in objetivos)
    print(f"carpetas a borrar      : {len(objetivos)}")
    if conservados:
        print(f"proyectos conservados  : {conservados} (más nuevos que {args.dias} días)")
    print(f"espacio a liberar      : {total / 1e9:.1f} GB")

    if not args.borrar:
        print("\nSIMULACRO: no se borró nada. Agregá --borrar para hacerlo.")
        for carpeta, peso in sorted(objetivos, key=lambda x: -x[1])[:10]:
            print(f"   {peso/1e9:6.2f} GB  {carpeta.relative_to(args.raiz)}")
        return 0

    borrado = 0
    fallos: list[str] = []
    for i, (carpeta, peso) in enumerate(objetivos, 1):
        try:
            shutil.rmtree(carpeta)
            borrado += peso
        except OSError as exc:
            fallos.append(f"{carpeta}: {exc}")
        if i % 50 == 0:
            print(f"   {i}/{len(objetivos)} -- {borrado/1e9:.1f} GB", flush=True)

    despues = _videos(args.raiz)
    print(f"\nliberado               : {borrado / 1e9:.1f} GB")
    print(f"videos al terminar     : {len(despues)}")
    if len(antes) != len(despues):
        perdidos = {p.name for p in antes} - {p.name for p in despues}
        print(f"¡ALERTA! faltan videos: {sorted(perdidos)[:10]}")
        return 1
    print("ningún video se tocó.")
    if fallos:
        print(f"\n{len(fallos)} carpeta(s) no se pudieron borrar:")
        for f in fallos[:5]:
            print(f"   {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
