import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteClipRepository,
    SqlitePublishLogRepository,
    SqliteMomentRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.clip import Clip, ClipStatus
from shorts_factory.domain.entities.moment import Moment
from shorts_factory.domain.entities.publication import Platform, Publication, PublicationStatus
from shorts_factory.domain.entities.video import Video
from shorts_factory.domain.use_cases.list_publishable_clips import ListPublishableClips


def _setup(conn: sqlite3.Connection, tmp_path: Path, missing_file: bool = False):
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    moments = SqliteMomentRepository(conn)
    clips = SqliteClipRepository(conn)
    log = SqlitePublishLogRepository(conn)

    channel = channels.add(Channel(youtube_channel_id="UC1", name="Canal"))
    video = videos.add(Video(channel_id=channel.id, youtube_video_id="v1", title="Video top"))
    moment = moments.add(
        Moment(video_id=video.id, start_seconds=0, end_seconds=30, impact_score=1.8, reason="picos de audio")
    )
    file_path = tmp_path / "clip.mp4"
    if not missing_file:
        file_path.write_bytes(b"x")
    clip = clips.add(
        Clip(moment_id=moment.id, file_path=str(file_path), duration_seconds=30, status=ClipStatus.READY)
    )
    use_case = ListPublishableClips(clips, moments, videos, channels, log)
    return use_case, clip, log


def test_lists_ready_clip_with_metadata(conn: sqlite3.Connection, tmp_path: Path) -> None:
    use_case, clip, _log = _setup(conn, tmp_path)

    items = use_case.execute()

    assert len(items) == 1
    item = items[0]
    assert item.clip_id == clip.id
    assert item.video_title == "Video top"
    assert item.channel_name == "Canal"
    assert item.file_exists is True
    assert item.published_on == frozenset()
    assert item.reason == "picos de audio"


def test_flags_missing_file(conn: sqlite3.Connection, tmp_path: Path) -> None:
    use_case, _clip, _log = _setup(conn, tmp_path, missing_file=True)

    items = use_case.execute()

    assert items[0].file_exists is False
    assert items[0].publishable is False


def test_tracks_already_published_platforms(conn: sqlite3.Connection, tmp_path: Path) -> None:
    use_case, clip, log = _setup(conn, tmp_path)
    log.add(
        Publication(clip_id=clip.id, platform=Platform.FACEBOOK, status=PublicationStatus.PUBLISHED)
    )

    items = use_case.execute()

    assert items[0].published_on == frozenset({"facebook"})


def test_suggests_waiting_within_24h_of_last_publish(conn: sqlite3.Connection, tmp_path: Path) -> None:
    use_case, clip, log = _setup(conn, tmp_path)
    log.add(
        Publication(
            clip_id=clip.id,
            platform=Platform.FACEBOOK,
            status=PublicationStatus.PUBLISHED,
            published_at=datetime.now() - timedelta(hours=2),
        )
    )

    assert use_case.should_suggest_waiting() is True


def test_does_not_suggest_waiting_after_24h(conn: sqlite3.Connection, tmp_path: Path) -> None:
    use_case, clip, log = _setup(conn, tmp_path)
    log.add(
        Publication(
            clip_id=clip.id,
            platform=Platform.FACEBOOK,
            status=PublicationStatus.PUBLISHED,
            published_at=datetime.now() - timedelta(hours=30),
        )
    )

    assert use_case.should_suggest_waiting() is False


def test_no_suggestion_when_nothing_published_yet(conn: sqlite3.Connection, tmp_path: Path) -> None:
    use_case, _clip, _log = _setup(conn, tmp_path)

    assert use_case.should_suggest_waiting() is False
    assert use_case.last_published_at() is None
