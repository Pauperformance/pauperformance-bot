from pauperformance_bot.entity.played_cards import PlayedCard


class PlayableDeck:
    def __init__(
        self,
        main,
        sideboard,
    ):
        self.main = main
        self.sideboard = sideboard

    def __str__(self):
        main = '\n'.join((repr(c) for c in self.main))
        sideboard = '\n'.join((repr(c) for c in self.sideboard))
        return f"Main:\n{main}\n\nSideboard:\n{sideboard}"

    def __repr__(self):
        return ' '.join((repr(c) for c in self.main)) + '|' + ' '.join((repr(c) for c in self.sideboard))

    def __hash__(self):
        return hash(repr(self))


if __name__ == '__main__':
    main = [PlayedCard(4, "Island"), PlayedCard(4, "Swamp")]
    sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    deck = PlayableDeck(main, sideboard)
    print(deck)
