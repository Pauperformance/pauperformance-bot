from msilib.schema import Error
from typing import Dict, Optional, Type

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader
from pauperformance_bot.service.mtg.downloader.mtgdecks import MtgdecksDeckDownloader
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DeckDownloaderService:
    """Service to download a deck from different sources given an input url"""

    _downloaders: Dict[str, Type[AbstractDeckDownloader]] = {
        "mtgdecks.net": MtgdecksDeckDownloader
    }

    @classmethod
    def from_url(cls, url: str) -> Optional[PlayableDeck]:
        """Downloads a deck from a given url.

        Args:
            url (str): url to fetch the deck list, e.g.
            "https://www.mtgtop8.com/mtgo?d=473002"

        Returns:
            Optional[PlayableDeck]: the representation of the deck or None.
        """
        for domain, cls in DeckDownloaderService._downloaders.items():
            if domain in url:
                logger.debug(f"Found specific downloader for {url}")
                return cls(url).download()
        # TODO check if we want to catch only specific errors here
        try:
            logger.debug(f"Using mtgo downloader for {url}")
            return MtgoDeckDownloader(url).download()
        except Error:
            return None
