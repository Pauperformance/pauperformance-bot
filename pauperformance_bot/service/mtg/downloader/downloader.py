from typing import Dict

import requests

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader
from pauperformance_bot.util.decklist_parser import MtgoDeckListParser
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.request import execute_http_request

logger = get_application_logger()


class MtgoDeckDownloader(AbstractDeckDownloader):
    """Generic downloader for lists in the "mtgo format".
    Most of the websites return simply a text list with one line per card.
    Each line is whitespace separated and it contains first the quantity and
    then the card name.
    The list starts from the main deck and the sideboard follows.
    The separator for the sideboard is

    Works with:
    - https://tappedout.net/mtg-decks/gobliny-combo/?fmt=dek&cb=1653244312
    - https://aetherhub.com/Deck/MtgoDeckExport/733379
    - https://www.mtgtop8.com/mtgo?d=473002
    """

    def __init__(self, url, headers: Dict = None) -> None:
        super().__init__(url)
        _headers = headers
        if not headers:
            _headers = {}
        self._headers = _headers

    def download(self) -> PlayableDeck:
        logger.debug(f"fetching deck list from {self._url}")
        resp = execute_http_request(requests.get, self._url, headers=self._headers)
        pl = "start"
        lines = []
        for ln in resp.text.strip().split("\n"):
            sl = ln.strip()
            sbl = sl.lower().startswith("sideboard")
            if sbl and pl:
                # some websites do not have a new line
                # before the sideboard separator
                lines.append("")
                pl = ""
            elif not sbl:
                lines.append(sl)
                pl = sl
        return MtgoDeckListParser().parse_lines(lines)
