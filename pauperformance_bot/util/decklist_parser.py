from abc import ABCMeta, abstractmethod

from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard


class DeckListParser(metaclass=ABCMeta):
    """Abstract parser class for deck lists"""

    MAIN_DECK_MAX = 60
    SIDEBOARD_MAX = 15

    @abstractmethod
    def parse_lines(self, lines) -> PlayableDeck:
        pass


class MtgoDeckListParser(DeckListParser):
    def parse_lines(self, lines) -> PlayableDeck:
        separator = lines.index("")
        maindeck = lines[:separator]
        maindeck.sort(key=lambda pc: pc.split(" ", maxsplit=1)[1])
        sideboard = lines[separator + 1 :]
        sideboard.sort(key=lambda pc: pc.split(" ", maxsplit=1)[1])
        return PlayableDeck(
            [PlayedCard(*(line.split(" ", maxsplit=1))) for line in maindeck],
            [PlayedCard(*(line.split(" ", maxsplit=1))) for line in sideboard],
        )
