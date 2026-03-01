from abc import ABCMeta, abstractmethod

from pauperformance_bot.entity.deck.playable import PlayableDeck


class AbstractDeckDownloader(metaclass=ABCMeta):
    def __init__(self, url: str) -> None:
        self._url = url

    @abstractmethod
    def download(self) -> PlayableDeck | None:
        pass
