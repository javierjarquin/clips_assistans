import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteClipRepository,
    SqliteDownloadRepository,
    SqliteMomentRepository,
    SqliteVideoRepository,
)
from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.clip import ClipStatus
from shorts_factory.domain.entities.download import Download, DownloadStatus
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.domain.use_cases.analyze_videos import AnalyzeVideos, ClipSettings
from shorts_factory.ports.analysis import AudioAnalyzerPort, AudioPeak, SceneDetectorPort
from shorts_factory.ports.inference_engine import InferenceEngine, TranscriptSegment
from shorts_factory.ports.video_processor import VideoProcessorPort


class FakeInference(InferenceEngine):
    def __init__(self, segments=None, error=None):
        self.segments = segments or []
        self.error = error

    def transcribe(self, media_path, language=None):
        if self.error:
            raise RuntimeError(self.error)
        return self.segments


class FakeAudio(AudioAnalyzerPort):
    def __init__(self, peaks=None):
        self.peaks = peaks or []

    def find_peaks(self, media_path):
        return self.peaks


class FakeScenes(SceneDetectorPort):
    def detect_scene_changes(self, media_path):
        return []


class FakeProcessor(VideoProcessorPort):
    def __init__(self, fail=False):
        self.fail = fail
        self.cuts = []

    def cut_segment(self, source, start_seconds, end_seconds, dest):
        return dest

    def to_vertical(self, source, dest):
        return dest

    def cut_vertical(self, source, start_seconds, end_seconds, dest):
        if self.fail:
            raise RuntimeError("encode falló")
        self.cuts.append((start_seconds, end_seconds))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"clip")
        return dest


@pytest.fixture()
def env(conn: sqlite3.Connection, tmp_path: Path):
    channels = SqliteChannelRepository(conn)
    videos = SqliteVideoRepository(conn)
    downloads = SqliteDownloadRepository(conn)
    moments = SqliteMomentRepository(conn)
    clips = SqliteClipRepository(conn)

    channel = channels.add(Channel(youtube_channel_id="UC1", name="Canal"))
    video = videos.add(
        Video(
            channel_id=channel.id,
            youtube_video_id="vid1",
            title="V1",
            duration_seconds=300,
            status=VideoStatus.DETECTED,
        )
    )
    videos.update_status(video.id, VideoStatus.DOWNLOADED)
    raw = tmp_path / "canal" / "vid1" / "raw.mp4"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"video")
    downloads.add(
        Download(
            video_id=video.id,
            file_path=str(raw),
            size_bytes=5,
            method="fake",
            status=DownloadStatus.COMPLETED,
            completed_at=datetime.now(),
        )
    )
    return videos, downloads, moments, clips, video, raw


def _use_case(env, inference=None, processor=None):
    videos, downloads, moments, clips, _, _ = env
    return AnalyzeVideos(
        videos,
        downloads,
        moments,
        clips,
        inference=inference or FakeInference(),
        audio_analyzer=FakeAudio([AudioPeak(120, 1.0), AudioPeak(122, 1.0), AudioPeak(124, 0.9)]),
        scene_detector=FakeScenes(),
        processor=processor or FakeProcessor(),
        clip_settings=ClipSettings(target_seconds=20),
    )


def test_analyze_creates_moments_and_ready_clips(env) -> None:
    videos, _, moments, clips, video, raw = env
    processor = FakeProcessor()

    report = _use_case(env, processor=processor).execute()

    assert [v.id for v in report.analyzed] == [video.id]
    assert videos.get(video.id).status is VideoStatus.ANALYZED
    stored_moments = moments.list_by_video(video.id)
    assert stored_moments, "debe registrar al menos un momento"
    ready = clips.list_by_status(ClipStatus.READY)
    assert len(ready) == report.clips_created > 0
    clip_file = Path(ready[0].file_path)
    assert clip_file.exists()
    assert clip_file.parent == raw.parent / "clips"


def test_clip_encode_failure_marks_clip_failed_video_analyzed(env) -> None:
    videos, _, _, clips, video, _ = env

    report = _use_case(env, processor=FakeProcessor(fail=True)).execute()

    assert videos.get(video.id).status is VideoStatus.ANALYZED
    assert report.clips_created == 0
    assert clips.list_by_status(ClipStatus.FAILED), "clip debe quedar en failed"


def test_inference_error_marks_video_error(env) -> None:
    videos, _, _, _, video, _ = env

    report = _use_case(env, inference=FakeInference(error="modelo no carga")).execute()

    assert videos.get(video.id).status is VideoStatus.ERROR
    assert report.failed and "modelo no carga" in report.failed[0][1]
