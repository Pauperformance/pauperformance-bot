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
        return '\n'.join((repr(c) for c in self.mainboard))

    @property
    def sideboard_mtggoldfish(self):
        return '\n'.join((repr(c) for c in self.sideboard))

    @property
    def len_mainboard(self):
        return sum(c.quantity for c in self.mainboard)

    @property
    def len_sideboard(self):
        return sum(c.quantity for c in self.sideboard)

    def is_legal(self, banned_cards):
        banned_cards = set(banned_cards)
        if len({c.card_name for c in self.mainboard} & banned_cards) != 0:
            return False
        if len({c.card_name for c in self.sideboard} & banned_cards) != 0:
            return False
        return True

    def __str__(self):
        return f"Main ({self.len_mainboard}):\n{self.mainboard_mtggoldfish}\n\n" \
               f"Sideboard ({self.len_sideboard}):\n{self.sideboard_mtggoldfish}"

    def __repr__(self):
        return ' '.join((repr(c) for c in self.mainboard)) + '|' + ' '.join((repr(c) for c in self.sideboard))

    def __hash__(self):
        return hash(repr(self))


if __name__ == '__main__':
    main = [PlayedCard(4, "Island"), PlayedCard(4, "Swamp")]
    sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    deck = PlayableDeck(main, sideboard)
    print(deck)
