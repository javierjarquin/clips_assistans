-- Esquema inicial: seis tablas (ver 03-Analisis-Tecnico §4)
-- Entidades lógicas: channels, videos, moments, clips
-- Eventos físicos (fallan y se reintentan): downloads, publish_log

CREATE TABLE IF NOT EXISTS channels (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    youtube_channel_id TEXT    NOT NULL UNIQUE,
    name               TEXT    NOT NULL,
    niche              TEXT,
    last_video_id      TEXT,
    active             INTEGER NOT NULL DEFAULT 1,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS videos (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id       INTEGER NOT NULL REFERENCES channels(id),
    youtube_video_id TEXT    NOT NULL UNIQUE,
    title            TEXT    NOT NULL,
    duration_seconds INTEGER,
    published_at     TEXT,
    status           TEXT    NOT NULL DEFAULT 'detected',
    detected_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS downloads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id      INTEGER NOT NULL REFERENCES videos(id),
    file_path     TEXT,
    size_bytes    INTEGER,
    method        TEXT,
    status        TEXT    NOT NULL DEFAULT 'pending',
    error_message TEXT,
    completed_at  TEXT
);

CREATE TABLE IF NOT EXISTS moments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id      INTEGER NOT NULL REFERENCES videos(id),
    start_seconds REAL    NOT NULL,
    end_seconds   REAL    NOT NULL,
    impact_score  REAL    NOT NULL,
    reason        TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS clips (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    moment_id        INTEGER NOT NULL REFERENCES moments(id),
    file_path        TEXT,
    duration_seconds REAL,
    format           TEXT    NOT NULL DEFAULT '9:16',
    status           TEXT    NOT NULL DEFAULT 'pending',
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS publish_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id       INTEGER NOT NULL REFERENCES clips(id),
    platform      TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'pending',
    post_url      TEXT,
    priority      INTEGER NOT NULL DEFAULT 0,
    retry_count   INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    published_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_videos_status      ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_channel     ON videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_downloads_video    ON downloads(video_id);
CREATE INDEX IF NOT EXISTS idx_moments_video      ON moments(video_id);
CREATE INDEX IF NOT EXISTS idx_clips_status       ON clips(status);
CREATE INDEX IF NOT EXISTS idx_publish_log_clip   ON publish_log(clip_id);
CREATE INDEX IF NOT EXISTS idx_publish_log_status ON publish_log(status);
