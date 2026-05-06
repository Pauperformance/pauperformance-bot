import requests
from constant.mtg.mtggoldfish import DECK_PROXY_API_ENDPOINT, DECK_PROXY_CLASS
from pyquery import PyQuery

from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader
from pauperformance_bot.util.request import execute_http_request


class MtggoldfishDeckDownloader(AbstractDeckDownloader):
    """Downloads a deck from mtggoldfish.com"""

    def __init__(self, url) -> None:
        super().__init__(url)

    def download(self) -> PlayableDeck:
        # they use Cloudflare to protect themselves, but the /proxy is not protected
        deck_id = self._url.split("/")[-1].split("#")[0]
        proxy_url = DECK_PROXY_API_ENDPOINT + deck_id
        response = execute_http_request(requests.get, proxy_url)
        pq = PyQuery(response.content)
        deck = pq(DECK_PROXY_CLASS).text()
        # clean up the deck-string by:
        # - stripping the first \n
        # - separating the sideboard from the main
        deck = deck.replace("sideboard", "").replace("\n", "", 1)
        deck = parse_playable_deck_from_lines(deck.split("\n"))
        return deck
