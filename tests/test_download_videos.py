import sqlite3
from pathlib import Path

import pytest

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteDownloadRepository,
    SqliteVideoRepository,
)
from shorts_factory.adapters.video_source.fallback_source import FallbackVideoSource
from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.download import DownloadStatus
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.domain.use_cases.download_videos import DownloadVideos, slugify
from tests.fakes import FakeVideoSource


@pytest.fixture()
def repos(conn: sqlite3.Connection):
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    downloads = SqliteDownloadRepository(conn)
    channel = channels.add(Channel(youtube_channel_id="UC1", name="Canal Niño Épico"))
    video = videos.add(Video(channel_id=channel.id, youtube_video_id="vid1", title="V1"))
    return channels, videos, downloads, video


def test_slugify_channel_names() -> None:
    assert slugify("Canal Niño Épico") == "canal-nino-epico"
    assert slugify("***") == "canal"


def test_successful_download_updates_state_and_paths(repos, tmp_path: Path) -> None:
    channels, videos, downloads, video = repos
    source = FakeVideoSource()
    use_case = DownloadVideos(videos, channels, downloads, source, data_dir=tmp_path)

    report = use_case.execute()

    assert [v.id for v in report.downloaded] == [video.id]
    assert videos.get(video.id).status is VideoStatus.DOWNLOADED
    expected = tmp_path / "canal-nino-epico" / "vid1" / "raw.mp4"
    assert expected.exists()

    rows = downloads.list_by_video(video.id)
    assert len(rows) == 1
    assert rows[0].status is DownloadStatus.COMPLETED
    assert rows[0].method == "fake"
    assert rows[0].size_bytes > 0
    assert rows[0].completed_at is not None


def test_failed_download_leaves_consistent_error_state(repos, tmp_path: Path) -> None:
    channels, videos, downloads, video = repos
    source = FakeVideoSource()
    source.fail_download = True
    use_case = DownloadVideos(videos, channels, downloads, source, data_dir=tmp_path)

    report = use_case.execute()

    assert report.downloaded == []
    assert videos.get(video.id).status is VideoStatus.ERROR
    rows = downloads.list_by_video(video.id)
    assert rows[0].status is DownloadStatus.FAILED
    assert rows[0].error_message == "fallo simulado"


def test_fallback_tries_sources_in_order(tmp_path: Path) -> None:
    failing = FakeVideoSource()
    failing.fail_download = True
    failing.name = "primera"
    working = FakeVideoSource()
    working.name = "segunda"
    fallback = FallbackVideoSource([failing, working])

    outcome = fallback.download("vidX", tmp_path / "raw.mp4")

    assert outcome.success is True
    assert failing.download_calls == ["vidX"]
    assert working.download_calls == ["vidX"]


def test_fallback_exhausted_reports_all_errors(tmp_path: Path) -> None:
    s1 = FakeVideoSource()
    s1.fail_download = True
    s1.name = "a"
    s2 = FakeVideoSource()
    s2.fail_download = True
    s2.name = "b"

    outcome = FallbackVideoSource([s1, s2]).download("vidX", tmp_path / "raw.mp4")

    assert outcome.success is False
    assert "a: fallo simulado" in outcome.error
    assert "b: fallo simulado" in outcome.error
