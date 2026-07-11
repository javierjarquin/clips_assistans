import sqlite3

import pytest

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.video import VideoStatus
from shorts_factory.domain.use_cases.register_channel import (
    ChannelAlreadyExistsError,
    RegisterChannel,
)
from shorts_factory.domain.use_cases.scan_channels import ScanChannels
from shorts_factory.ports.video_source import VideoMetadata
from tests.fakes import FakeVideoSource


def _meta(video_id: str) -> VideoMetadata:
    return VideoMetadata(youtube_video_id=video_id, title=f"Video {video_id}")


@pytest.fixture()
def setup(conn: sqlite3.Connection):
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    source = FakeVideoSource()
    RegisterChannel(channels).execute("UC_test", "Canal Test", "reacciones")
    scan = ScanChannels(channels, videos, source)
    return channels, videos, source, scan


def test_register_duplicate_channel_rejected(conn: sqlite3.Connection) -> None:
    channels = SqliteChannelRepository(conn)
    RegisterChannel(channels).execute("UC_dup", "Uno")
    with pytest.raises(ChannelAlreadyExistsError):
        RegisterChannel(channels).execute("UC_dup", "Dos")


def test_first_scan_sets_baseline_without_videos(setup) -> None:
    channels, videos, source, scan = setup
    source.feeds["UC_test"] = [_meta("v3"), _meta("v2"), _meta("v1")]

    results = scan.execute()

    assert results[0].baseline_set is True
    assert results[0].new_videos == []
    assert channels.get_by_youtube_id("UC_test").last_video_id == "v3"
    assert videos.list_by_status(VideoStatus.DETECTED) == []


def test_new_videos_detected_after_baseline(setup) -> None:
    channels, videos, source, scan = setup
    source.feeds["UC_test"] = [_meta("v3"), _meta("v2"), _meta("v1")]
    scan.execute()  # línea base en v3

    source.feeds["UC_test"] = [_meta("v5"), _meta("v4"), _meta("v3"), _meta("v2")]
    results = scan.execute()

    detected = results[0].new_videos
    assert [v.youtube_video_id for v in detected] == ["v5", "v4"]
    assert all(v.status is VideoStatus.DETECTED for v in detected)
    assert channels.get_by_youtube_id("UC_test").last_video_id == "v5"


def test_rescan_without_news_does_not_duplicate(setup) -> None:
    _, videos, source, scan = setup
    source.feeds["UC_test"] = [_meta("v3")]
    scan.execute()
    source.feeds["UC_test"] = [_meta("v4"), _meta("v3")]
    scan.execute()

    results = scan.execute()  # sin cambios en el feed

    assert results[0].new_videos == []
    assert len(videos.list_by_status(VideoStatus.DETECTED)) == 1


def test_source_error_does_not_break_scan(setup) -> None:
    class ExplodingSource(FakeVideoSource):
        def list_recent_videos(self, youtube_channel_id: str, limit: int = 10):
            raise RuntimeError("red caída")

    channels, videos, _, _ = setup
    scan = ScanChannels(channels, videos, ExplodingSource())

    results = scan.execute()

    assert results[0].error == "red caída"
    assert results[0].new_videos == []
