import sqlite3
from pathlib import Path

import pytest

from shorts_factory.infrastructure.database import run_migrations

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    run_migrations(connection, MIGRATIONS_DIR)
    return connection
