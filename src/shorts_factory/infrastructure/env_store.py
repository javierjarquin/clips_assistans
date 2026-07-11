"""Lectura/escritura del archivo .env del proyecto.

La GUI guarda aquí las credenciales para que el usuario no edite variables a
mano. Se preservan comentarios y orden: las claves existentes se actualizan en
su línea; las nuevas se agregan al final. Tras guardar se recarga el entorno
del proceso (override) para que el siguiente contenedor vea los valores nuevos.
"""

import re
from pathlib import Path

from dotenv import load_dotenv

from shorts_factory.infrastructure.config import _PROJECT_ROOT

ENV_PATH = _PROJECT_ROOT / ".env"

_LINE_RE = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=(?P<value>.*)$")


def read_env(path: Path = ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _LINE_RE.match(line)
        if match and not line.lstrip().startswith("#"):
            values[match.group("key")] = match.group("value").strip().strip('"').strip("'")
    return values


def save_env(updates: dict[str, str], path: Path = ENV_PATH) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    pending = dict(updates)
    output: list[str] = []
    for line in lines:
        match = _LINE_RE.match(line)
        if match and not line.lstrip().startswith("#") and match.group("key") in pending:
            key = match.group("key")
            output.append(f"{key}={pending.pop(key)}")
        else:
            output.append(line)
    for key, value in pending.items():
        output.append(f"{key}={value}")
    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    load_dotenv(dotenv_path=path, override=True)
