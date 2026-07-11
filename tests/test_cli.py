from pathlib import Path

from typer.testing import CliRunner

from shorts_factory.cli.main import app

runner = CliRunner()

EXPECTED_COMMANDS = ["init", "status", "channel", "scan", "download", "analyze", "publish", "run"]


def test_help_lists_planned_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in EXPECTED_COMMANDS:
        assert command in result.output


def test_init_creates_database(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SF_DB_PATH", str(db_path))
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output
    assert db_path.exists()
    assert "Tablas (6)" in result.output
