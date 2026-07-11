"""Conexión SQLite y runner de migraciones."""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def get_connection(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path) -> list[str]:
    """Aplica en orden los .sql pendientes y devuelve los nombres aplicados."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        " filename TEXT PRIMARY KEY,"
        " applied_at TEXT NOT NULL DEFAULT (datetime('now')))"
    )
    applied = {
        row[0] for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()
    }
    executed: list[str] = []
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        if sql_file.name in applied:
            continue
        logger.info("Aplicando migración %s", sql_file.name)
        conn.executescript(sql_file.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations (filename) VALUES (?)", (sql_file.name,))
        conn.commit()
        executed.append(sql_file.name)
    return executed


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
        " AND name NOT LIKE 'sqlite_%' AND name != 'schema_migrations' ORDER BY name"
    )
    return [row[0] for row in rows]
