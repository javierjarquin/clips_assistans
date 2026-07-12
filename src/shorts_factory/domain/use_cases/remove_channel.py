from shorts_factory.ports.repository import ChannelRepository


class ChannelNotFoundError(Exception):
    pass


class RemoveChannel:
    def __init__(self, channel_repo: ChannelRepository) -> None:
        self._channels = channel_repo

    def execute(self, channel_id: int) -> bool:
        """Elimina el canal. Devuelve True si se borró, False si se desactivó."""
        if self._channels.get(channel_id) is None:
            raise ChannelNotFoundError(f"No existe el canal #{channel_id}")
        return self._channels.remove(channel_id)
