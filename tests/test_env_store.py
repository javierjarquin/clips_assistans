from pathlib import Path

from shorts_factory.infrastructure.env_store import read_env, save_env


def test_save_creates_file_and_read_roundtrip(tmp_path: Path) -> None:
    env = tmp_path / ".env"

    save_env({"SF_META_PAGE_ID": "12345", "SF_X_ACCESS_TOKEN": "secreto"}, path=env)

    values = read_env(env)
    assert values["SF_META_PAGE_ID"] == "12345"
    assert values["SF_X_ACCESS_TOKEN"] == "secreto"


def test_save_preserves_comments_and_updates_in_place(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "# Configuración de prueba\n"
        "SF_META_PAGE_ID=viejo\n"
        "# otra sección\n"
        "SF_LOG_LEVEL=INFO\n",
        encoding="utf-8",
    )

    save_env({"SF_META_PAGE_ID": "nuevo", "SF_PLATFORMS": "facebook,x"}, path=env)

    content = env.read_text(encoding="utf-8")
    assert "# Configuración de prueba" in content
    assert "# otra sección" in content
    assert content.index("SF_META_PAGE_ID=nuevo") < content.index("SF_LOG_LEVEL=INFO")
    values = read_env(env)
    assert values["SF_META_PAGE_ID"] == "nuevo"
    assert values["SF_LOG_LEVEL"] == "INFO"
    assert values["SF_PLATFORMS"] == "facebook,x"


def test_read_ignores_comments_and_strips_quotes(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text('# SF_IGNORADA=x\nSF_TOKEN="entre comillas"\n', encoding="utf-8")

    values = read_env(env)

    assert "SF_IGNORADA" not in values
    assert values["SF_TOKEN"] == "entre comillas"
