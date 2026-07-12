import sqlite3
from pathlib import Path

import pytest

from shorts_factory.adapters.publishers.x_adapter import strip_links
from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteClipRepository,
    SqliteDownloadRepository,
    SqliteMomentRepository,
    SqlitePublishLogRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.clip import Clip, ClipStatus
from shorts_factory.domain.entities.moment import Moment
from shorts_factory.domain.entities.publication import Platform, PublicationStatus
from shorts_factory.domain.entities.video import Video
from shorts_factory.domain.use_cases.publish_clips import PublishClips
from shorts_factory.ports.publisher import PublisherPort, PublishOutcome


class FakePublisher(PublisherPort):
    def __init__(self, platform: Platform, fail: bool = False):
        self._platform = platform
        self.fail = fail
        self.calls: list[tuple[Path, str]] = []

    @property
    def platform(self) -> Platform:
        return self._platform

    def publish(self, clip_path: Path, caption: str) -> PublishOutcome:
        self.calls.append((clip_path, caption))
        if self.fail:
            return PublishOutcome(success=False, error="api caída")
        return PublishOutcome(success=True, post_url=f"https://{self._platform.value}/post/1")


@pytest.fixture()
def env(conn: sqlite3.Connection, tmp_path: Path):
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    moments = SqliteMomentRepository(conn)
    clips = SqliteClipRepository(conn)
    log = SqlitePublishLogRepository(conn)

    channel = channels.add(Channel(youtube_channel_id="UC1", name="Canal"))
    video = videos.add(Video(channel_id=channel.id, youtube_video_id="v1", title="Título del video"))
    moment = moments.add(Moment(video_id=video.id, start_seconds=10, end_seconds=40, impact_score=2.5))
    clip_file = tmp_path / "clip.mp4"
    clip_file.write_bytes(b"clip")
    clip = clips.add(
        Clip(
            moment_id=moment.id,
            file_path=str(clip_file),
            duration_seconds=30,
            status=ClipStatus.READY,
        )
    )
    return clips, moments, videos, log, clip


def test_publish_all_platforms_with_priority_order(env) -> None:
    clips, moments, videos, log, clip = env
    tiktok = FakePublisher(Platform.TIKTOK)
    facebook = FakePublisher(Platform.FACEBOOK)
    use_case = PublishClips(
        clips, moments, videos, log,
        publishers={Platform.FACEBOOK: facebook, Platform.TIKTOK: tiktok},
        priorities={Platform.TIKTOK: 40, Platform.FACEBOOK: 20},
    )

    report = use_case.execute()

    assert report.enqueued == 2
    assert len(report.published) == 2
    # TikTok (prioridad 40) procesado antes que Facebook (20)
    assert [p.platform for p in report.published] == [Platform.TIKTOK, Platform.FACEBOOK]
    assert facebook.calls[0][1] == "Título del video"  # caption = título
    published = log.list_by_status(PublicationStatus.PUBLISHED)
    assert len(published) == 2
    assert all(p.post_url for p in published)


def test_rerun_does_not_duplicate_queue(env) -> None:
    clips, moments, videos, log, clip = env
    publisher = FakePublisher(Platform.FACEBOOK)
    use_case = PublishClips(
        clips, moments, videos, log, publishers={Platform.FACEBOOK: publisher}
    )

    use_case.execute()
    report2 = use_case.execute()

    assert report2.enqueued == 0
    assert len(publisher.calls) == 1  # no re-publica lo ya publicado


def test_failure_retries_until_limit(env) -> None:
    clips, moments, videos, log, clip = env
    publisher = FakePublisher(Platform.X, fail=True)
    use_case = PublishClips(
        clips, moments, videos, log, publishers={Platform.X: publisher}, max_retries=3
    )

    use_case.execute()  # intento 1 -> PENDING
    use_case.execute()  # intento 2 -> PENDING
    assert log.list_by_status(PublicationStatus.PENDING), "aún reintentable"

    use_case.execute()  # intento 3 -> FAILED definitivo

    failed = log.list_by_status(PublicationStatus.FAILED)
    assert len(failed) == 1
    assert failed[0].retry_count == 3
    assert failed[0].error_message == "api caída"
    assert len(publisher.calls) == 3


def test_one_platform_failure_does_not_block_others(env) -> None:
    clips, moments, videos, log, clip = env
    ok = FakePublisher(Platform.INSTAGRAM)
    broken = FakePublisher(Platform.TIKTOK, fail=True)
    use_case = PublishClips(
        clips, moments, videos, log,
        publishers={Platform.INSTAGRAM: ok, Platform.TIKTOK: broken},
        priorities={Platform.TIKTOK: 40, Platform.INSTAGRAM: 30},
    )

    report = use_case.execute()

    assert [p.platform for p in report.published] == [Platform.INSTAGRAM]
    assert [p.platform for p in report.failed] == [Platform.TIKTOK]


def test_execute_with_clip_id_publishes_only_that_clip(conn: sqlite3.Connection, tmp_path: Path) -> None:
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    moments = SqliteMomentRepository(conn)
    clips = SqliteClipRepository(conn)
    log = SqlitePublishLogRepository(conn)

    channel = channels.add(Channel(youtube_channel_id="UC1", name="Canal"))
    video = videos.add(Video(channel_id=channel.id, youtube_video_id="v1", title="Video"))
    moment = moments.add(Moment(video_id=video.id, start_seconds=0, end_seconds=10, impact_score=1))
    file_a = tmp_path / "a.mp4"
    file_a.write_bytes(b"a")
    file_b = tmp_path / "b.mp4"
    file_b.write_bytes(b"b")
    clip_a = clips.add(Clip(moment_id=moment.id, file_path=str(file_a), status=ClipStatus.READY))
    clip_b = clips.add(Clip(moment_id=moment.id, file_path=str(file_b), status=ClipStatus.READY))

    publisher = FakePublisher(Platform.FACEBOOK)
    use_case = PublishClips(clips, moments, videos, log, publishers={Platform.FACEBOOK: publisher})

    report = use_case.execute(clip_id=clip_a.id)

    assert report.enqueued == 1
    assert len(publisher.calls) == 1
    # el segundo clip sigue sin publicación pendiente: no se tocó
    assert log.list_by_clip(clip_b.id) == []


def test_strip_links_removes_urls() -> None:
    result = strip_links("Mira esto https://ejemplo.com/x y www.otro.com fin")
    assert "http" not in result and "ejemplo.com" not in result and "otro.com" not in result
    assert result.startswith("Mira esto")
    assert strip_links("sin enlaces") == "sin enlaces"
