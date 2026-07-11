from shorts_factory.domain.entities.channel import Channel
from shorts_factory.ports.repository import ChannelRepository


class ChannelAlreadyExistsError(Exception):
    pass


class RegisterChannel:
    def __init__(self, channel_repo: ChannelRepository) -> None:
        self._channels = channel_repo

    def execute(self, youtube_channel_id: str, name: str, niche: str | None = None) -> Channel:
        if self._channels.get_by_youtube_id(youtube_channel_id):
            raise ChannelAlreadyExistsError(f"El canal {youtube_channel_id} ya está registrado")
        return self._channels.add(
            Channel(youtube_channel_id=youtube_channel_id, name=name, niche=niche)
        )
