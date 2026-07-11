"""Adaptador SQLite de los repositorios. Migración futura a PostgreSQL = nuevo adaptador."""

import sqlite3
from datetime import datetime

from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.clip import Clip, ClipStatus
from shorts_factory.domain.entities.download import Download, DownloadStatus
from shorts_factory.domain.entities.moment import Moment
from shorts_factory.domain.entities.publication import Platform, Publication, PublicationStatus
from shorts_factory.domain.entities.video import Video, VideoStatus
from shorts_factory.ports.repository import (
    ChannelRepository,
    ClipRepository,
    DownloadRepository,
    MomentRepository,
    PublishLogRepository,
    VideoRepository,
)


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _iso(value: datetime | None) -> str | None:
    return value.isoformat(sep=" ") if value else None


class SqliteChannelRepository(ChannelRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, channel: Channel) -> Channel:
        cur = self._conn.execute(
            "INSERT INTO channels (youtube_channel_id, name, niche, last_video_id, active)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                channel.youtube_channel_id,
                channel.name,
                channel.niche,
                channel.last_video_id,
                int(channel.active),
            ),
        )
        self._conn.commit()
        channel.id = cur.lastrowid
        return channel

    def get(self, channel_id: int) -> Channel | None:
        row = self._conn.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        return self._to_entity(row) if row else None

    def get_by_youtube_id(self, youtube_channel_id: str) -> Channel | None:
        row = self._conn.execute(
            "SELECT * FROM channels WHERE youtube_channel_id = ?", (youtube_channel_id,)
        ).fetchone()
        return self._to_entity(row) if row else None

    def list_all(self, active_only: bool = False) -> list[Channel]:
        sql = "SELECT * FROM channels"
        if active_only:
            sql += " WHERE active = 1"
        return [self._to_entity(r) for r in self._conn.execute(sql + " ORDER BY id")]

    def update_last_video(self, channel_id: int, youtube_video_id: str) -> None:
        self._conn.execute(
            "UPDATE channels SET last_video_id = ? WHERE id = ?", (youtube_video_id, channel_id)
        )
        self._conn.commit()

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Channel:
        return Channel(
            id=row["id"],
            youtube_channel_id=row["youtube_channel_id"],
            name=row["name"],
            niche=row["niche"],
            last_video_id=row["last_video_id"],
            active=bool(row["active"]),
            created_at=_dt(row["created_at"]),
        )


class SqliteVideoRepository(VideoRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, video: Video) -> Video:
        cur = self._conn.execute(
            "INSERT INTO videos"
            " (channel_id, youtube_video_id, title, duration_seconds, published_at, status)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                video.channel_id,
                video.youtube_video_id,
                video.title,
                video.duration_seconds,
                _iso(video.published_at),
                video.status.value,
            ),
        )
        self._conn.commit()
        video.id = cur.lastrowid
        return video

    def get(self, video_id: int) -> Video | None:
        row = self._conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
        return self._to_entity(row) if row else None

    def get_by_youtube_id(self, youtube_video_id: str) -> Video | None:
        row = self._conn.execute(
            "SELECT * FROM videos WHERE youtube_video_id = ?", (youtube_video_id,)
        ).fetchone()
        return self._to_entity(row) if row else None

    def list_by_status(self, status: VideoStatus) -> list[Video]:
        rows = self._conn.execute(
            "SELECT * FROM videos WHERE status = ? ORDER BY id", (status.value,)
        )
        return [self._to_entity(r) for r in rows]

    def update_status(self, video_id: int, status: VideoStatus) -> None:
        self._conn.execute("UPDATE videos SET status = ? WHERE id = ?", (status.value, video_id))
        self._conn.commit()

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Video:
        return Video(
            id=row["id"],
            channel_id=row["channel_id"],
            youtube_video_id=row["youtube_video_id"],
            title=row["title"],
            duration_seconds=row["duration_seconds"],
            published_at=_dt(row["published_at"]),
            status=VideoStatus(row["status"]),
            detected_at=_dt(row["detected_at"]),
        )


class SqliteDownloadRepository(DownloadRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, download: Download) -> Download:
        cur = self._conn.execute(
            "INSERT INTO downloads"
            " (video_id, file_path, size_bytes, method, status, error_message, completed_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                download.video_id,
                download.file_path,
                download.size_bytes,
                download.method,
                download.status.value,
                download.error_message,
                _iso(download.completed_at),
            ),
        )
        self._conn.commit()
        download.id = cur.lastrowid
        return download

    def update(self, download: Download) -> None:
        self._conn.execute(
            "UPDATE downloads SET file_path = ?, size_bytes = ?, method = ?, status = ?,"
            " error_message = ?, completed_at = ? WHERE id = ?",
            (
                download.file_path,
                download.size_bytes,
                download.method,
                download.status.value,
                download.error_message,
                _iso(download.completed_at),
                download.id,
            ),
        )
        self._conn.commit()

    def list_by_video(self, video_id: int) -> list[Download]:
        rows = self._conn.execute(
            "SELECT * FROM downloads WHERE video_id = ? ORDER BY id", (video_id,)
        )
        return [self._to_entity(r) for r in rows]

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Download:
        return Download(
            id=row["id"],
            video_id=row["video_id"],
            file_path=row["file_path"],
            size_bytes=row["size_bytes"],
            method=row["method"],
            status=DownloadStatus(row["status"]),
            error_message=row["error_message"],
            completed_at=_dt(row["completed_at"]),
        )


class SqliteMomentRepository(MomentRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, moment: Moment) -> Moment:
        cur = self._conn.execute(
            "INSERT INTO moments (video_id, start_seconds, end_seconds, impact_score, reason)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                moment.video_id,
                moment.start_seconds,
                moment.end_seconds,
                moment.impact_score,
                moment.reason,
            ),
        )
        self._conn.commit()
        moment.id = cur.lastrowid
        return moment

    def get(self, moment_id: int) -> Moment | None:
        row = self._conn.execute("SELECT * FROM moments WHERE id = ?", (moment_id,)).fetchone()
        return self._to_entity(row) if row else None

    def list_by_video(self, video_id: int) -> list[Moment]:
        rows = self._conn.execute(
            "SELECT * FROM moments WHERE video_id = ? ORDER BY impact_score DESC", (video_id,)
        )
        return [self._to_entity(r) for r in rows]

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Moment:
        return Moment(
            id=row["id"],
            video_id=row["video_id"],
            start_seconds=row["start_seconds"],
            end_seconds=row["end_seconds"],
            impact_score=row["impact_score"],
            reason=row["reason"],
            created_at=_dt(row["created_at"]),
        )


class SqliteClipRepository(ClipRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, clip: Clip) -> Clip:
        cur = self._conn.execute(
            "INSERT INTO clips (moment_id, file_path, duration_seconds, format, status)"
            " VALUES (?, ?, ?, ?, ?)",
            (clip.moment_id, clip.file_path, clip.duration_seconds, clip.format, clip.status.value),
        )
        self._conn.commit()
        clip.id = cur.lastrowid
        return clip

    def get(self, clip_id: int) -> Clip | None:
        row = self._conn.execute("SELECT * FROM clips WHERE id = ?", (clip_id,)).fetchone()
        return self._to_entity(row) if row else None

    def update(self, clip: Clip) -> None:
        self._conn.execute(
            "UPDATE clips SET file_path = ?, duration_seconds = ?, format = ?, status = ?"
            " WHERE id = ?",
            (clip.file_path, clip.duration_seconds, clip.format, clip.status.value, clip.id),
        )
        self._conn.commit()

    def update_status(self, clip_id: int, status: ClipStatus) -> None:
        self._conn.execute("UPDATE clips SET status = ? WHERE id = ?", (status.value, clip_id))
        self._conn.commit()

    def list_by_status(self, status: ClipStatus) -> list[Clip]:
        rows = self._conn.execute(
            "SELECT * FROM clips WHERE status = ? ORDER BY id", (status.value,)
        )
        return [self._to_entity(r) for r in rows]

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Clip:
        return Clip(
            id=row["id"],
            moment_id=row["moment_id"],
            file_path=row["file_path"],
            duration_seconds=row["duration_seconds"],
            format=row["format"],
            status=ClipStatus(row["status"]),
            created_at=_dt(row["created_at"]),
        )


class SqlitePublishLogRepository(PublishLogRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, publication: Publication) -> Publication:
        cur = self._conn.execute(
            "INSERT INTO publish_log"
            " (clip_id, platform, status, post_url, priority, retry_count, error_message,"
            " published_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                publication.clip_id,
                publication.platform.value,
                publication.status.value,
                publication.post_url,
                publication.priority,
                publication.retry_count,
                publication.error_message,
                _iso(publication.published_at),
            ),
        )
        self._conn.commit()
        publication.id = cur.lastrowid
        return publication

    def update(self, publication: Publication) -> None:
        self._conn.execute(
            "UPDATE publish_log SET status = ?, post_url = ?, priority = ?, retry_count = ?,"
            " error_message = ?, published_at = ? WHERE id = ?",
            (
                publication.status.value,
                publication.post_url,
                publication.priority,
                publication.retry_count,
                publication.error_message,
                _iso(publication.published_at),
                publication.id,
            ),
        )
        self._conn.commit()

    def list_by_status(self, status: PublicationStatus) -> list[Publication]:
        rows = self._conn.execute(
            "SELECT * FROM publish_log WHERE status = ? ORDER BY priority DESC, id",
            (status.value,),
        )
        return [self._to_entity(r) for r in rows]

    def list_by_clip(self, clip_id: int) -> list[Publication]:
        rows = self._conn.execute(
            "SELECT * FROM publish_log WHERE clip_id = ? ORDER BY id", (clip_id,)
        )
        return [self._to_entity(r) for r in rows]

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Publication:
        return Publication(
            id=row["id"],
            clip_id=row["clip_id"],
            platform=Platform(row["platform"]),
            status=PublicationStatus(row["status"]),
            post_url=row["post_url"],
            priority=row["priority"],
            retry_count=row["retry_count"],
            error_message=row["error_message"],
            published_at=_dt(row["published_at"]),
        )
