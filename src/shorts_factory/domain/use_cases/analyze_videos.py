"""Análisis de videos descargados: señales -> momentos -> clips verticales.

Estados: downloaded -> analyzing -> analyzed | error. Los momentos quedan en
`moments` (memoria de qué consideró interesante el sistema y por qué) y los
archivos cortados en `clips`.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from shorts_factory.domain.entities.clip import Clip, ClipStatus
from shorts_factory.domain.entities.moment import Moment
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.domain.services.impact_scorer import score_moments
from shorts_factory.ports.analysis import AudioAnalyzerPort, SceneDetectorPort
from shorts_factory.ports.inference_engine import InferenceEngine
from shorts_factory.ports.repository import (
    ClipRepository,
    DownloadRepository,
    MomentRepository,
    VideoRepository,
)
from shorts_factory.ports.video_processor import VideoProcessorPort

logger = logging.getLogger(__name__)


@dataclass
class AnalyzeReport:
    analyzed: list[Video] = field(default_factory=list)
    clips_created: int = 0
    failed: list[tuple[Video, str]] = field(default_factory=list)


@dataclass(frozen=True)
class ClipSettings:
    min_seconds: float = 10.0
    max_seconds: float = 60.0
    target_seconds: float = 30.0
    max_per_video: int = 4
    language: str | None = None


class AnalyzeVideos:
    def __init__(
        self,
        video_repo: VideoRepository,
        download_repo: DownloadRepository,
        moment_repo: MomentRepository,
        clip_repo: ClipRepository,
        inference: InferenceEngine,
        audio_analyzer: AudioAnalyzerPort,
        scene_detector: SceneDetectorPort,
        processor: VideoProcessorPort,
        clip_settings: ClipSettings | None = None,
    ) -> None:
        self._videos = video_repo
        self._downloads = download_repo
        self._moments = moment_repo
        self._clips = clip_repo
        self._inference = inference
        self._audio = audio_analyzer
        self._scenes = scene_detector
        self._processor = processor
        self._settings = clip_settings or ClipSettings()

    def execute(self) -> AnalyzeReport:
        report = AnalyzeReport()
        for video in self._videos.list_by_status(VideoStatus.DOWNLOADED):
            self._analyze_one(video, report)
        return report

    def _analyze_one(self, video: Video, report: AnalyzeReport) -> None:
        raw_path = self._raw_path(video)
        if raw_path is None:
            self._fail(video, report, "sin descarga completada registrada")
            return

        self._videos.update_status(video.id, VideoStatus.ANALYZING)
        try:
            transcript = self._inference.transcribe(raw_path, language=self._settings.language)
            audio_peaks = self._audio.find_peaks(raw_path)
            scene_changes = self._scenes.detect_scene_changes(raw_path)

            duration = float(video.duration_seconds or 0)
            if duration <= 0:
                ends = [s.end_seconds for s in transcript]
                ends += [p.time_seconds for p in audio_peaks]
                ends += scene_changes
                duration = max(ends, default=0.0)

            candidates = score_moments(
                duration_seconds=duration,
                transcript=transcript,
                audio_peaks=audio_peaks,
                scene_changes=scene_changes,
                min_clip_seconds=self._settings.min_seconds,
                max_clip_seconds=self._settings.max_seconds,
                target_clip_seconds=self._settings.target_seconds,
                max_moments=self._settings.max_per_video,
            )
            logger.info("%s: %d momento(s) candidatos", video.youtube_video_id, len(candidates))

            clips_dir = raw_path.parent / "clips"
            for candidate in candidates:
                moment = self._moments.add(
                    Moment(
                        video_id=video.id,
                        start_seconds=candidate.start_seconds,
                        end_seconds=candidate.end_seconds,
                        impact_score=candidate.impact_score,
                        reason=candidate.reason,
                    )
                )
                clip_path = clips_dir / f"clip_{moment.id:03d}.mp4"
                clip = self._clips.add(Clip(moment_id=moment.id))
                try:
                    self._processor.cut_vertical(
                        raw_path, candidate.start_seconds, candidate.end_seconds, clip_path
                    )
                except Exception as exc:  # noqa: BLE001 — un clip fallido no anula los demás
                    logger.error("Corte falló (momento %d): %s", moment.id, exc)
                    self._clips.update_status(clip.id, ClipStatus.FAILED)
                    continue
                clip.file_path = str(clip_path)
                clip.duration_seconds = candidate.end_seconds - candidate.start_seconds
                clip.status = ClipStatus.READY
                self._clips.update(clip)
                report.clips_created += 1

            self._videos.update_status(video.id, VideoStatus.ANALYZED)
            report.analyzed.append(video)
        except Exception as exc:  # noqa: BLE001 — el video queda en error, el lote sigue
            self._fail(video, report, str(exc))

    def _raw_path(self, video: Video) -> Path | None:
        for download in reversed(self._downloads.list_by_video(video.id)):
            if download.file_path and download.status.value == "completed":
                path = Path(download.file_path)
                if path.exists():
                    return path
        return None

    def _fail(self, video: Video, report: AnalyzeReport, error: str) -> None:
        logger.error("Análisis falló para %s: %s", video.youtube_video_id, error)
        self._videos.update_status(video.id, VideoStatus.ERROR)
        report.failed.append((video, error))
