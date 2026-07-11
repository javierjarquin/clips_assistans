"""Configuración por variables de entorno, con soporte de archivo .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto: src/shorts_factory/infrastructure/config.py -> 3 niveles arriba de src/
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    database_path: Path
    data_dir: Path
    migrations_dir: Path
    log_level: str
    log_file: Path | None
    scan_limit: int
    ytdlp_cookies_browser: str | None
    # Etapa 3 — análisis
    whisper_model: str
    whisper_cpu_threads: int
    whisper_language: str | None
    ffmpeg_path: str
    video_encoder: str
    clip_min_seconds: float
    clip_max_seconds: float
    clip_target_seconds: float
    max_clips_per_video: int
    # Etapa 4 — publicación
    enabled_platforms: tuple[str, ...]
    platform_priorities: dict[str, int]
    publish_max_retries: int
    # Meta: app (para renovar el token de 60 días) + página + IG business
    meta_graph_version: str
    meta_app_id: str | None
    meta_app_secret: str | None
    meta_page_id: str | None
    meta_page_access_token: str | None
    meta_ig_user_id: str | None
    # TikTok: OAuth2 con refresh (access 24h); el refresh token rota
    tiktok_client_key: str | None
    tiktok_client_secret: str | None
    tiktok_refresh_token: str | None
    tiktok_access_token: str | None
    tiktok_privacy_level: str
    # X: OAuth2 user context con PKCE (access 2h); refresh de un solo uso
    x_client_id: str | None
    x_client_secret: str | None
    x_refresh_token: str | None
    x_access_token: str | None
    # Etapa 5 — orquestación
    pipeline_interval_minutes: int


def load_settings() -> Settings:
    load_dotenv()
    log_file = os.getenv("SF_LOG_FILE", "").strip()
    cookies_browser = os.getenv("SF_YTDLP_COOKIES_BROWSER", "").strip()
    language = os.getenv("SF_WHISPER_LANGUAGE", "").strip()
    return Settings(
        database_path=Path(os.getenv("SF_DB_PATH", "shorts_factory.db")),
        data_dir=Path(os.getenv("SF_DATA_DIR", "data")),
        migrations_dir=Path(os.getenv("SF_MIGRATIONS_DIR", _PROJECT_ROOT / "migrations")),
        log_level=os.getenv("SF_LOG_LEVEL", "INFO").upper(),
        log_file=Path(log_file) if log_file else None,
        scan_limit=int(os.getenv("SF_SCAN_LIMIT", "10")),
        ytdlp_cookies_browser=cookies_browser or None,
        whisper_model=os.getenv("SF_WHISPER_MODEL", "small"),
        whisper_cpu_threads=int(os.getenv("SF_WHISPER_CPU_THREADS", "0")),
        whisper_language=language or None,
        ffmpeg_path=os.getenv("SF_FFMPEG_PATH", "ffmpeg"),
        video_encoder=os.getenv("SF_VIDEO_ENCODER", "auto"),
        clip_min_seconds=float(os.getenv("SF_CLIP_MIN_SECONDS", "10")),
        clip_max_seconds=float(os.getenv("SF_CLIP_MAX_SECONDS", "60")),
        clip_target_seconds=float(os.getenv("SF_CLIP_TARGET_SECONDS", "30")),
        max_clips_per_video=int(os.getenv("SF_MAX_CLIPS_PER_VIDEO", "4")),
        enabled_platforms=_platforms(os.getenv("SF_PLATFORMS", "")),
        platform_priorities={
            "tiktok": int(os.getenv("SF_PRIORITY_TIKTOK", "40")),
            "instagram": int(os.getenv("SF_PRIORITY_INSTAGRAM", "30")),
            "facebook": int(os.getenv("SF_PRIORITY_FACEBOOK", "20")),
            "x": int(os.getenv("SF_PRIORITY_X", "10")),
        },
        publish_max_retries=int(os.getenv("SF_PUBLISH_MAX_RETRIES", "3")),
        meta_graph_version=os.getenv("SF_META_GRAPH_VERSION", "v23.0"),
        meta_app_id=os.getenv("SF_META_APP_ID") or None,
        meta_app_secret=os.getenv("SF_META_APP_SECRET") or None,
        meta_page_id=os.getenv("SF_META_PAGE_ID") or None,
        meta_page_access_token=os.getenv("SF_META_PAGE_ACCESS_TOKEN") or None,
        meta_ig_user_id=os.getenv("SF_META_IG_USER_ID") or None,
        tiktok_client_key=os.getenv("SF_TIKTOK_CLIENT_KEY") or None,
        tiktok_client_secret=os.getenv("SF_TIKTOK_CLIENT_SECRET") or None,
        tiktok_refresh_token=os.getenv("SF_TIKTOK_REFRESH_TOKEN") or None,
        tiktok_access_token=os.getenv("SF_TIKTOK_ACCESS_TOKEN") or None,
        tiktok_privacy_level=os.getenv("SF_TIKTOK_PRIVACY_LEVEL", "SELF_ONLY"),
        x_client_id=os.getenv("SF_X_CLIENT_ID") or None,
        x_client_secret=os.getenv("SF_X_CLIENT_SECRET") or None,
        x_refresh_token=os.getenv("SF_X_REFRESH_TOKEN") or None,
        x_access_token=os.getenv("SF_X_ACCESS_TOKEN") or None,
        pipeline_interval_minutes=int(os.getenv("SF_PIPELINE_INTERVAL_MINUTES", "30")),
    )


def _platforms(raw: str) -> tuple[str, ...]:
    return tuple(p.strip().lower() for p in raw.split(",") if p.strip())
