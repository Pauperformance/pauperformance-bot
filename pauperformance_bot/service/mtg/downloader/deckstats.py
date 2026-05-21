from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.deckstats import DeckstatsService
from pauperformance_bot.service.mtg.downloader.abstract import AbstractDeckDownloader
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DeckstatsDeckDownloader(AbstractDeckDownloader):
    """Downloads a deck from deckstats.net.

    Supports URLs of the form:
        https://deckstats.net/decks/{owner_id}/{saved_id}-{slug}
    """

    def __init__(self, url) -> None:
        super().__init__(url)
        parts = url.rstrip("/").split("/")
        self._owner_id = parts[-2]
        self._saved_id = parts[-1].split("-")[0]

    def download(self) -> PlayableDeck:
        logger.debug(
            f"Fetching deckstats deck {self._saved_id} "
            f"for owner {self._owner_id}..."
        )
        service = DeckstatsService(owner_id=self._owner_id)
        deck_json = service.get_deck(self._saved_id, use_cache=False)
        return service.to_playable_deck(deck_json)
