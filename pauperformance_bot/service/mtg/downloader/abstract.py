from abc import ABCMeta, abstractmethod
from typing import Optional

from pauperformance_bot.entity.deck.playable import PlayableDeck


class AbstractDeckDownloader(metaclass=ABCMeta):
    def __init__(self, url) -> None:
        self._url = url

    @abstractmethod
    def download(self) -> Optional[PlayableDeck]:
        pass
