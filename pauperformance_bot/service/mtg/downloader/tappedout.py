from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader


class TappedOutDeckDownloader(AbstractDeckDownloader):
    def download_deck_from_url(self, url) -> PlayableDeck:
        # e.g. https://tappedout.net/mtg-decks/gobliny-combo/
        pass  # TODO
