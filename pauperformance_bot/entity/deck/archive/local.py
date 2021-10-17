from os.path import sep

from pauperformance_bot.entity.deck.archive.abstract import Archive
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class Local(Archive):
    def __init__(
        self,
        name,
        creation_date,
        deck_id,
        decks_path,
    ):
        super().__init__(name, creation_date, deck_id)
        self.decks_path = decks_path

    @property
    def url(self):
        return f"{self.decks_path}{sep}{self.deck_id}"
