import sqlite3
from pathlib import Path

import pytest

from shorts_factory.infrastructure.database import list_tables, run_migrations

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"

EXPECTED_TABLES = {"channels", "videos", "downloads", "moments", "clips", "publish_log"}


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def test_migrations_create_six_tables(conn: sqlite3.Connection) -> None:
    applied = run_migrations(conn, MIGRATIONS_DIR)
    assert applied, "debe aplicar al menos una migración"
    assert set(list_tables(conn)) == EXPECTED_TABLES


def test_migrations_are_idempotent(conn: sqlite3.Connection) -> None:
    run_migrations(conn, MIGRATIONS_DIR)
    assert run_migrations(conn, MIGRATIONS_DIR) == []
