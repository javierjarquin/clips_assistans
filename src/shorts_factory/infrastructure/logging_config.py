"""Configuración base de logging: consola siempre, archivo opcional."""

import logging
from pathlib import Path

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"


def setup_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=level, format=_FORMAT, handlers=handlers)
