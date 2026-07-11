"""Composición de dependencias: instancia adaptadores y los provee a los casos de uso.

Sin framework de DI — una clase explícita con propiedades perezosas basta al inicio.
"""

import sqlite3
from functools import cached_property

from shorts_factory.adapters.repository.sqlite_adapter import (
    SqliteChannelRepository,
    SqliteClipRepository,
    SqliteDownloadRepository,
    SqliteMomentRepository,
    SqlitePublishLogRepository,
    SqliteVideoRepository,
)
from shorts_factory.adapters.inference.audio_analyzer import LibrosaAudioAnalyzer
from shorts_factory.adapters.inference.cpu_whisper_adapter import FasterWhisperEngine
from shorts_factory.adapters.inference.scene_detector import PySceneDetectAdapter
from shorts_factory.adapters.processing.ffmpeg_adapter import FFmpegProcessor
from shorts_factory.adapters.publishers.meta_adapter import (
    FacebookReelsPublisher,
    InstagramReelsPublisher,
)
from shorts_factory.adapters.publishers.tiktok_adapter import TikTokPublisher
from shorts_factory.adapters.publishers.x_adapter import XPublisher
from shorts_factory.adapters.video_source.fallback_source import FallbackVideoSource
from shorts_factory.adapters.video_source.ytdlp_adapter import YtDlpVideoSource
from shorts_factory.domain.entities.publication import Platform
from shorts_factory.domain.use_cases.analyze_videos import AnalyzeVideos, ClipSettings
from shorts_factory.domain.use_cases.download_videos import DownloadVideos
from shorts_factory.domain.use_cases.publish_clips import PublishClips
from shorts_factory.domain.use_cases.register_channel import RegisterChannel
from shorts_factory.domain.use_cases.run_pipeline import RunPipeline
from shorts_factory.domain.use_cases.scan_channels import ScanChannels
from shorts_factory.ports.publisher import PublisherPort
from shorts_factory.infrastructure.config import Settings
from shorts_factory.infrastructure.database import get_connection, run_migrations
from shorts_factory.infrastructure.ffmpeg_locator import resolve_ffmpeg
from shorts_factory.ports.video_source import VideoSourcePort


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @cached_property
    def connection(self) -> sqlite3.Connection:
        return get_connection(self.settings.database_path)

    def init_db(self) -> list[str]:
        """Crea la base de datos y aplica las migraciones pendientes."""
        return run_migrations(self.connection, self.settings.migrations_dir)

    @cached_property
    def channel_repo(self) -> SqliteChannelRepository:
        return SqliteChannelRepository(self.connection)

    @cached_property
    def video_repo(self) -> SqliteVideoRepository:
        return SqliteVideoRepository(self.connection)

    @cached_property
    def download_repo(self) -> SqliteDownloadRepository:
        return SqliteDownloadRepository(self.connection)

    @cached_property
    def moment_repo(self) -> SqliteMomentRepository:
        return SqliteMomentRepository(self.connection)

    @cached_property
    def clip_repo(self) -> SqliteClipRepository:
        return SqliteClipRepository(self.connection)

    @cached_property
    def publish_log_repo(self) -> SqlitePublishLogRepository:
        return SqlitePublishLogRepository(self.connection)

    # --- Adaptadores externos ---

    @cached_property
    def video_source(self) -> VideoSourcePort:
        """Estrategia multi-API: web, cliente android, y cookies de navegador si hay."""
        sources: list[VideoSourcePort] = [YtDlpVideoSource()]
        android = YtDlpVideoSource(extractor_args={"youtube": {"player_client": ["android"]}})
        android.name = "yt-dlp-android"
        sources.append(android)
        if self.settings.ytdlp_cookies_browser:
            with_cookies = YtDlpVideoSource(
                cookies_from_browser=self.settings.ytdlp_cookies_browser
            )
            with_cookies.name = "yt-dlp-cookies"
            sources.append(with_cookies)
        return FallbackVideoSource(sources)

    # --- Casos de uso ---

    @cached_property
    def register_channel(self) -> RegisterChannel:
        return RegisterChannel(self.channel_repo)

    @cached_property
    def scan_channels(self) -> ScanChannels:
        return ScanChannels(
            self.channel_repo,
            self.video_repo,
            self.video_source,
            scan_limit=self.settings.scan_limit,
        )

    @cached_property
    def download_videos(self) -> DownloadVideos:
        return DownloadVideos(
            self.video_repo,
            self.channel_repo,
            self.download_repo,
            self.video_source,
            data_dir=self.settings.data_dir,
        )

    @cached_property
    def ffmpeg_path(self) -> str:
        return resolve_ffmpeg(self.settings.ffmpeg_path)

    @cached_property
    def analyze_videos(self) -> AnalyzeVideos:
        return AnalyzeVideos(
            self.video_repo,
            self.download_repo,
            self.moment_repo,
            self.clip_repo,
            inference=FasterWhisperEngine(
                model_size=self.settings.whisper_model,
                cpu_threads=self.settings.whisper_cpu_threads,
            ),
            audio_analyzer=LibrosaAudioAnalyzer(ffmpeg_path=self.ffmpeg_path),
            scene_detector=PySceneDetectAdapter(),
            processor=FFmpegProcessor(
                ffmpeg_path=self.ffmpeg_path, encoder=self.settings.video_encoder
            ),
            clip_settings=ClipSettings(
                min_seconds=self.settings.clip_min_seconds,
                max_seconds=self.settings.clip_max_seconds,
                target_seconds=self.settings.clip_target_seconds,
                max_per_video=self.settings.max_clips_per_video,
                language=self.settings.whisper_language,
            ),
        )

    @cached_property
    def publishers(self) -> dict[Platform, PublisherPort]:
        """Solo las plataformas habilitadas en SF_PLATFORMS entran a la cola.

        TikTok y X rotan sus refresh tokens en cada renovación: el callback
        on_tokens los persiste al .env para que el siguiente arranque viva.
        """
        from shorts_factory.infrastructure.env_store import save_env

        s = self.settings
        available: dict[Platform, PublisherPort] = {
            Platform.FACEBOOK: FacebookReelsPublisher(
                s.meta_page_id, s.meta_page_access_token, s.meta_graph_version
            ),
            Platform.INSTAGRAM: InstagramReelsPublisher(
                s.meta_ig_user_id, s.meta_page_access_token, s.meta_graph_version
            ),
            Platform.TIKTOK: TikTokPublisher(
                s.tiktok_client_key,
                s.tiktok_client_secret,
                s.tiktok_refresh_token,
                access_token=s.tiktok_access_token,
                privacy_level=s.tiktok_privacy_level,
                on_tokens=save_env,
            ),
            Platform.X: XPublisher(
                s.x_client_id,
                s.x_client_secret,
                s.x_refresh_token,
                access_token=s.x_access_token,
                on_tokens=save_env,
            ),
        }
        return {
            platform: publisher
            for platform, publisher in available.items()
            if platform.value in s.enabled_platforms
        }

    @cached_property
    def run_pipeline(self) -> RunPipeline:
        return RunPipeline(
            self.scan_channels,
            self.download_videos,
            self.analyze_videos,
            publish=self.publish_clips if self.publishers else None,
        )

    @cached_property
    def publish_clips(self) -> PublishClips:
        priorities = {
            Platform(name): value
            for name, value in self.settings.platform_priorities.items()
        }
        return PublishClips(
            self.clip_repo,
            self.moment_repo,
            self.video_repo,
            self.publish_log_repo,
            publishers=self.publishers,
            priorities=priorities,
            max_retries=self.settings.publish_max_retries,
        )
