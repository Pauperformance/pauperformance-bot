from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader


class AetherhubDeckDownloader(AbstractDeckDownloader):
    def download_deck_from_url(self, url) -> PlayableDeck:
        # e.g. https://aetherhub.com/Deck/grixis-control-733379
        pass  # TODO
