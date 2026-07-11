import sqlite3
from pathlib import Path

import pytest

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.infrastructure.database import run_migrations

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    run_migrations(connection, MIGRATIONS_DIR)
    return connection


def test_channel_roundtrip(conn: sqlite3.Connection) -> None:
    repo = SqliteChannelRepository(conn)
    saved = repo.add(Channel(youtube_channel_id="UC123", name="Canal Prueba", niche="reacciones"))
    assert saved.id is not None

    fetched = repo.get_by_youtube_id("UC123")
    assert fetched is not None
    assert fetched.name == "Canal Prueba"
    assert fetched.active is True
    assert fetched.created_at is not None

    repo.update_last_video(saved.id, "vid001")
    assert repo.get(saved.id).last_video_id == "vid001"


def test_video_status_flow(conn: sqlite3.Connection) -> None:
    channel = SqliteChannelRepository(conn).add(Channel(youtube_channel_id="UC1", name="C"))
    repo = SqliteVideoRepository(conn)
    video = repo.add(Video(channel_id=channel.id, youtube_video_id="v1", title="Video 1"))

    assert repo.get_by_youtube_id("v1").status is VideoStatus.DETECTED
    assert [v.id for v in repo.list_by_status(VideoStatus.DETECTED)] == [video.id]

    repo.update_status(video.id, VideoStatus.DOWNLOADED)
    assert repo.get(video.id).status is VideoStatus.DOWNLOADED
    assert repo.list_by_status(VideoStatus.DETECTED) == []
