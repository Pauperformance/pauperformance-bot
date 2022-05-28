from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader


class MtgdecksDeckDownloader(AbstractDeckDownloader):
    def download_deck_from_url(self, url) -> PlayableDeck:
        # e.g. https://mtgdecks.net/Pauper/burn-decklist-by-thormyn-1380435
        pass  # TODO
