from abc import ABC, abstractmethod

from shorts_factory.domain.entities.channel import Channel
from shorts_factory.domain.entities.clip import Clip, ClipStatus
from shorts_factory.domain.entities.download import Download
from shorts_factory.domain.entities.moment import Moment
from shorts_factory.domain.entities.publication import Publication, PublicationStatus
from shorts_factory.domain.entities.video import Video, VideoStatus


class ChannelRepository(ABC):
    @abstractmethod
    def add(self, channel: Channel) -> Channel: ...

    @abstractmethod
    def get(self, channel_id: int) -> Channel | None: ...

    @abstractmethod
    def get_by_youtube_id(self, youtube_channel_id: str) -> Channel | None: ...

    @abstractmethod
    def list_all(self, active_only: bool = False) -> list[Channel]: ...

    @abstractmethod
    def update_last_video(self, channel_id: int, youtube_video_id: str) -> None: ...


class VideoRepository(ABC):
    @abstractmethod
    def add(self, video: Video) -> Video: ...

    @abstractmethod
    def get(self, video_id: int) -> Video | None: ...

    @abstractmethod
    def get_by_youtube_id(self, youtube_video_id: str) -> Video | None: ...

    @abstractmethod
    def list_by_status(self, status: VideoStatus) -> list[Video]: ...

    @abstractmethod
    def update_status(self, video_id: int, status: VideoStatus) -> None: ...


class DownloadRepository(ABC):
    @abstractmethod
    def add(self, download: Download) -> Download: ...

    @abstractmethod
    def update(self, download: Download) -> None: ...

    @abstractmethod
    def list_by_video(self, video_id: int) -> list[Download]: ...


class MomentRepository(ABC):
    @abstractmethod
    def add(self, moment: Moment) -> Moment: ...

    @abstractmethod
    def get(self, moment_id: int) -> Moment | None: ...

    @abstractmethod
    def list_by_video(self, video_id: int) -> list[Moment]: ...


class ClipRepository(ABC):
    @abstractmethod
    def add(self, clip: Clip) -> Clip: ...

    @abstractmethod
    def get(self, clip_id: int) -> Clip | None: ...

    @abstractmethod
    def update(self, clip: Clip) -> None: ...

    @abstractmethod
    def update_status(self, clip_id: int, status: ClipStatus) -> None: ...

    @abstractmethod
    def list_by_status(self, status: ClipStatus) -> list[Clip]: ...


class PublishLogRepository(ABC):
    @abstractmethod
    def add(self, publication: Publication) -> Publication: ...

    @abstractmethod
    def update(self, publication: Publication) -> None: ...

    @abstractmethod
    def list_by_status(self, status: PublicationStatus) -> list[Publication]: ...

    @abstractmethod
    def list_by_clip(self, clip_id: int) -> list[Publication]: ...
