import requests

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader
from pauperformance_bot.util.decklist_parser import MtgoDeckListParser
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.request import execute_http_request

logger = get_application_logger()


class MoxfieldDeckDownloader(AbstractDeckDownloader):
    """Downloads a deck from https://www.moxfield.com/"""

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
        deck_id = self._url.split("/")[-1]
        logger.debug(f"Querying moxfield deck {deck_id}...")
        api_url = f"https://api2.moxfield.com/v3/decks/all/{deck_id}"
        logger.debug(f"{api_url}")
        resp = execute_http_request(
            requests.get,
            api_url,
            headers=self._downloader._headers,
        )
        logger.debug("Fetched deck.")
        deck = resp.json()
        logger.debug(f"Author name: {deck['name']}")
        lines = []
        for card in deck["boards"]["mainboard"]["cards"].values():
            quantity = card["quantity"]
            name = card["card"]["name"]
            lines.append(f"{quantity} {name}")
        lines.append("")
        for card in deck["boards"]["sideboard"]["cards"].values():
            quantity = card["quantity"]
            name = card["card"]["name"]
            lines.append(f"{quantity} {name}")
        return MtgoDeckListParser().parse_lines(lines)
