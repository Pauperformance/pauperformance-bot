from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader


class Mtgtop8DeckDownloader(AbstractDeckDownloader):
    def download_deck_from_url(self, url) -> PlayableDeck:
        # e.g. https://www.mtgtop8.com/event?e=36290&d=473001&f=PAU
        pass  # TODO
