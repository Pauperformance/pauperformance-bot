from pauperformance_bot.constant.mtggoldfish import (
    DECK_API_ENDPOINT,
    DECK_DOWNLOAD_API_ENDPOINT,
)
from pauperformance_bot.util.time import pretty_str


class ListedMTGGoldfishDeck:
    def __init__(
        self,
        name,
        format_,
        creation_date,
        visibility,
        deck_id,
    ):
        # On MTGGoldfish the format of the name is:
        # Archetype name p12e_code.revision.player | Name of the set (set_code)
        self.name = name
        self.format_ = format_
        self.creation_date = creation_date
        self.visibility = visibility
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
    def url(self):
        return f"{DECK_API_ENDPOINT}/{self.deck_id}"

    @property
    def download_txt_url(self):
        return f"{DECK_DOWNLOAD_API_ENDPOINT}/{self.deck_id}"

    @property
    def download_tabletop_url(self):
        return (
            f"{DECK_DOWNLOAD_API_ENDPOINT}/{self.deck_id}"
            f"?output=mtggoldfish&amp;type=tabletop"
        )

    @property
    def download_arena_url(self):
        return (
            f"{DECK_DOWNLOAD_API_ENDPOINT}/{self.deck_id}"
            f"?output=mtggoldfish&amp;type=arena"
        )

    @property
    def download_mtgo_url(self):
        return (
            f"{DECK_DOWNLOAD_API_ENDPOINT}/{self.deck_id}"
            f"?output=mtggoldfish&amp;type=online"
        )

    def __str__(self):
        return (
            f"name: {self.name}; "
            f"format: {self.format_}; "
            f"creation_date: {pretty_str(self.creation_date)}; "
            f"visibility: {self.visibility}; "
            f"deck_id: {self.deck_id}; "
            f"url: {self.url}"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.deck_id)

    def __eq__(self, other):
        return self.deck_id == other.deck_id
