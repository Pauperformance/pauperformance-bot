from os.path import sep

from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class LocalArchivedDeck(AbstractArchivedDeck):
    def __init__(
        self,
        name: str,
        creation_date: int,
        deck_id: str,
        decks_path: str,
    ) -> None:
        super().__init__(name, creation_date, deck_id)
        self.decks_path = decks_path

    @property
    def url(self) -> str:
        return f"{self.decks_path}{sep}{self.deck_id}"
