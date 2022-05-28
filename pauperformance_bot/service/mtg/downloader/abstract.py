from abc import ABCMeta, abstractmethod

from pauperformance_bot.entity.deck.playable import PlayableDeck


class AbstractDeckDownloader(metaclass=ABCMeta):
    @abstractmethod
    def download_deck_from_url(self, url) -> PlayableDeck:
        pass
