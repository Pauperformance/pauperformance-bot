from abc import ABCMeta, abstractmethod

from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import pretty_str

logger = get_application_logger()


class AbstractArchivedDeck(metaclass=ABCMeta):
    def __init__(
        self,
        name,
        creation_date,
        deck_id,
    ):
        # The format of the name in the Archive is:
        # Archetype name p12e_code.revision.player | Name of the set (set_code)
        self.name = name
        self.creation_date = creation_date
        self.deck_id = deck_id

    @property
    def p12e_name(self):
        p12e_name, friendly_name = self.name.split(" | ")
        return p12e_name

    @property
    def archetype(self):
        p12e_name, friendly_name = self.name.split(" | ")
        archetype_and_p12e_code = p12e_name.split(".")[0]
        return archetype_and_p12e_code.rsplit(" ", maxsplit=1)[0]

    @property
    def owner_name(self):
        p12e_name, friendly_name = self.name.split(" | ")
        return ".".join(p12e_name.rsplit(".")[2:])

    @property
    def p12e_code(self):
        p12e_name, friendly_name = self.name.split(" | ")
        archetype_and_p12e_code = p12e_name.split(".")[0]
        return archetype_and_p12e_code.rsplit(" ", maxsplit=1)[1]

    @property
    @abstractmethod
    def url(self):  # TODO: rename to URI
        pass

    def __str__(self):
        return (
            f"name: {self.name}; "
            f"creation_date: {pretty_str(self.creation_date)}; "
            f"deck_id: {self.deck_id}; "
            f"url: {self.url}"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.deck_id)

    def __eq__(self, other):
        return self.deck_id == other.deck_id
