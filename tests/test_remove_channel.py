import sqlite3

import pytest

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.video import Video
from shorts_factory.domain.use_cases.register_channel import RegisterChannel
from shorts_factory.domain.use_cases.remove_channel import ChannelNotFoundError, RemoveChannel


def test_remove_channel_without_videos_deletes_it(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    channel = RegisterChannel(channels).execute("UC_a", "Canal A")

    deleted = RemoveChannel(channels).execute(channel.id)

    assert deleted is True
    assert channels.get(channel.id) is None


def test_remove_channel_with_videos_deactivates_instead(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    channel = RegisterChannel(channels).execute("UC_b", "Canal B")
    videos.add(Video(channel_id=channel.id, youtube_video_id="v1", title="Video 1"))

    deleted = RemoveChannel(channels).execute(channel.id)

    assert deleted is False
    remaining = channels.get(channel.id)
    assert remaining is not None
    assert remaining.active is False


def test_remove_unknown_channel_raises(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    with pytest.raises(ChannelNotFoundError):
        RemoveChannel(channels).execute(999)
