import sqlite3

import pytest

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.video import VideoStatus
from shorts_factory.domain.use_cases.bootstrap_channel import (
    BootstrapChannelWithLatestVideo,
    ChannelNotFoundError,
)
from shorts_factory.domain.use_cases.register_channel import RegisterChannel
from shorts_factory.ports.video_source import VideoMetadata
from tests.fakes import FakeVideoSource


def _meta(video_id: str) -> VideoMetadata:
    return VideoMetadata(youtube_video_id=video_id, title=f"Video {video_id}")


def test_bootstrap_queues_latest_video_as_detected(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    source = FakeVideoSource()
    channel = RegisterChannel(channels).execute("UC_new", "Canal Nuevo")
    source.feeds["UC_new"] = [_meta("newest"), _meta("older")]

    use_case = BootstrapChannelWithLatestVideo(channels, videos, source)
    video = use_case.execute(channel.id)

    assert video is not None
    assert video.youtube_video_id == "newest"
    assert video.status == VideoStatus.DETECTED
    assert [v.id for v in videos.list_by_status(VideoStatus.DETECTED)] == [video.id]
    # a diferencia del scan normal, la línea base también queda fijada
    assert channels.get(channel.id).last_video_id == "newest"


def test_bootstrap_is_idempotent_if_called_twice(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    source = FakeVideoSource()
    channel = RegisterChannel(channels).execute("UC_new", "Canal Nuevo")
    source.feeds["UC_new"] = [_meta("newest")]
    use_case = BootstrapChannelWithLatestVideo(channels, videos, source)

    first = use_case.execute(channel.id)
    second = use_case.execute(channel.id)

    assert first.id == second.id
    assert len(videos.list_by_status(VideoStatus.DETECTED)) == 1


def test_bootstrap_channel_without_videos_returns_none(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    source = FakeVideoSource()
    channel = RegisterChannel(channels).execute("UC_empty", "Canal Vacío")

    use_case = BootstrapChannelWithLatestVideo(channels, videos, source)
    result = use_case.execute(channel.id)

    assert result is None


def test_bootstrap_unknown_channel_raises(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    source = FakeVideoSource()
    use_case = BootstrapChannelWithLatestVideo(channels, videos, source)

    with pytest.raises(ChannelNotFoundError):
        use_case.execute(999)
