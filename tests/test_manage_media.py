import sqlite3
from pathlib import Path

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
from shorts_factory.domain.entities.download import Download, DownloadStatus
from shorts_factory.domain.entities.moment import Moment
from shorts_factory.domain.entities.publication import Platform, Publication
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.domain.use_cases.manage_media import (
    DeleteClipFile,
    DeleteVideoFiles,
    ListMediaAssets,
)


def _setup(conn: sqlite3.Connection, tmp_path: Path):
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    downloads = SqliteDownloadRepository(conn)
    moments = SqliteMomentRepository(conn)
    clips = SqliteClipRepository(conn)
    log = SqlitePublishLogRepository(conn)

    channel = channels.add(Channel(youtube_channel_id="UC1", name="Canal"))
    video = videos.add(
        Video(channel_id=channel.id, youtube_video_id="v1", title="Video", status=VideoStatus.ANALYZED)
    )
    video_dir = tmp_path / "canal" / "v1"
    video_dir.mkdir(parents=True)
    raw = video_dir / "raw.mp4"
    raw.write_bytes(b"raw-bytes")
    downloads.add(
        Download(video_id=video.id, file_path=str(raw), size_bytes=9, status=DownloadStatus.COMPLETED)
    )
    moment = moments.add(Moment(video_id=video.id, start_seconds=0, end_seconds=10, impact_score=1))
    clips_dir = video_dir / "clips"
    clips_dir.mkdir()
    clip_file = clips_dir / "clip_1.mp4"
    clip_file.write_bytes(b"clip-bytes")
    clip = clips.add(
        Clip(moment_id=moment.id, file_path=str(clip_file), status=ClipStatus.READY)
    )
    return channels, videos, downloads, moments, clips, log, video, clip, raw, clip_file


def test_list_media_assets_reports_sizes_and_existence(conn: sqlite3.Connection, tmp_path: Path) -> None:
    _channels, videos, downloads, _moments, clips, _log, video, clip, raw, clip_file = _setup(
        conn, tmp_path
    )
    use_case = ListMediaAssets(videos, _channels, downloads, clips)

    assets = use_case.execute()

    assert len(assets) == 1
    asset = assets[0]
    assert asset.video_id == video.id
    assert asset.raw_exists is True
    assert asset.raw_size_bytes == raw.stat().st_size
    assert len(asset.clips) == 1
    assert asset.clips[0].exists is True
    assert asset.total_size_bytes == raw.stat().st_size + clip_file.stat().st_size


def test_delete_video_files_removes_folder_and_db_rows(conn: sqlite3.Connection, tmp_path: Path) -> None:
    channels, videos, downloads, moments, clips, log, video, clip, raw, clip_file = _setup(
        conn, tmp_path
    )
    log.add(Publication(clip_id=clip.id, platform=Platform.FACEBOOK))
    use_case = DeleteVideoFiles(videos, downloads)

    deleted = use_case.execute(video.id)

    assert deleted is True
    assert not raw.parent.exists()  # carpeta completa del video, no solo el archivo
    assert videos.get(video.id) is None
    assert clips.get(clip.id) is None
    assert moments.list_by_video(video.id) == []
    assert log.list_by_clip(clip.id) == []


def test_delete_video_files_cleans_db_even_if_files_already_gone(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    channels, videos, downloads, moments, clips, log, video, clip, raw, clip_file = _setup(
        conn, tmp_path
    )
    # Simula lo que le pasó al usuario: borró la carpeta a mano, la BD quedó huérfana
    import shutil

    shutil.rmtree(raw.parent)
    use_case = DeleteVideoFiles(videos, downloads)

    deleted = use_case.execute(video.id)

    assert deleted is False  # no había nada que borrar en disco
    assert videos.get(video.id) is None  # pero el registro huérfano sí se limpió


def test_delete_clip_file_removes_file_and_row(conn: sqlite3.Connection, tmp_path: Path) -> None:
    _channels, _videos, _downloads, _moments, clips, log, _video, clip, _raw, clip_file = _setup(
        conn, tmp_path
    )
    log.add(Publication(clip_id=clip.id, platform=Platform.FACEBOOK))
    use_case = DeleteClipFile(clips)

    deleted = use_case.execute(clip.id)

    assert deleted is True
    assert not clip_file.exists()
    assert clips.get(clip.id) is None
    assert log.list_by_clip(clip.id) == []


def test_delete_clip_file_unknown_clip_returns_false(conn: sqlite3.Connection) -> None:
    clips = SqliteClipRepository(conn)
    assert DeleteClipFile(clips).execute(999) is False
