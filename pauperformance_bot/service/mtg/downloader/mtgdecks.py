from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader


class MtgdecksDeckDownloader(AbstractDeckDownloader):
    """Downloads a deck from mtgdecks.net"""

    def __init__(self, url) -> None:
        super().__init__(url)
        self._downloader = MtgoDeckDownloader(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0)"
                + " Gecko/20100101 Firefox/101.0"
            },
        )

    def download(self) -> PlayableDeck:
        # they use Cloudflare to protect themselves, it seems like setting the
        # User-Agent header is enough to bypass that
        # curl -v \
        # https://mtgdecks.net/Pauper/burn-decklist-by-thormyn-1380435/txt \
        # -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) \
        # Gecko/20100101 Firefox/101.0'
        return self._downloader.download()
