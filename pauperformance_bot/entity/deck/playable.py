from pauperformance_bot.entity.played_cards import PlayedCard


class PlayableDeck:
    def __init__(
        self,
        mainboard,
        sideboard,
    ):
        self.mainboard = mainboard
        self.sideboard = sideboard

    @property
    def mainboard_mtggoldfish(self):
        return "\n".join((repr(c) for c in self.mainboard))

    @property
    def sideboard_mtggoldfish(self):
        return "\n".join((repr(c) for c in self.sideboard))

    @property
    def len_mainboard(self):
        return sum(c.quantity for c in self.mainboard)

    @property
    def len_sideboard(self):
        return sum(c.quantity for c in self.sideboard)

    def is_legal(self, banned_cards_names):
        banned_cards_names = set(banned_cards_names)
        if (
            len({c.card_name for c in self.mainboard} & banned_cards_names)
            != 0
        ):
            return False
        if (
            len({c.card_name for c in self.sideboard} & banned_cards_names)
            != 0
        ):
            return False
        return True

    def __str__(self):
        return (
            f"Main ({self.len_mainboard}):\n{self.mainboard_mtggoldfish}\n\n"
            f"Sideboard ({self.len_sideboard}):\n{self.sideboard_mtggoldfish}"
        )

    def __repr__(self):
        return (
            " ".join((repr(c) for c in self.mainboard))
            + "|"
            + " ".join((repr(c) for c in self.sideboard))
        )

    def __hash__(self):
        return hash(repr(self))


def parse_playable_deck_from_lines(lines):
    separator = lines.index("")
    maindeck = lines[:separator]
    sideboard = lines[separator + 1 : -1]
    return PlayableDeck(
        [PlayedCard(*(line.split(" ", maxsplit=1))) for line in maindeck],
        [PlayedCard(*(line.split(" ", maxsplit=1))) for line in sideboard],
    )
