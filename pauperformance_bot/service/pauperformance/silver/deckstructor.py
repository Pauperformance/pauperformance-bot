import re

from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class Deckstructor:

    @staticmethod
    def __merge_deck_sideboard(deck, sideboard):
        cards = deck.copy()

        for key, value in sideboard.items():
            if key in cards:
                cards[key] += value
            else:
                cards[key] = value

        return cards

    @staticmethod
    def __validate_pool(cards, pool):
        for card in cards:
            if card not in pool:
                logger.warning(f"{card} not in pool")

    @staticmethod
    def extract_deck(text, pool) -> PlayableDeck:
        # TODO: autogenerate pool from Scryfall with all pauper cards (legal and banned)
        mainboard = {}
        sideboard = {}
        pattern = re.compile(r"^(\d+) (.+)")

        lines = text.split("\n")

        is_deck = False
        is_mainboard = True

        for line in lines:
            result = pattern.search(line.strip())
            if result:
                is_deck = True
                if is_mainboard:
                    mainboard[result.group(2)] = int(result.group(1))
                else:
                    sideboard[result.group(2)] = int(result.group(1))
            elif is_deck and not result:
                is_mainboard = False

        cards = Deckstructor.__merge_deck_sideboard(mainboard, sideboard)
        Deckstructor.__validate_pool(cards, pool)

        deck = PlayableDeck(
            mainboard=[
                PlayedCard(quantity, name) for name, quantity in mainboard.items()
            ],
            sideboard=[
                PlayedCard(quantity, name) for name, quantity in sideboard.items()
            ],
        )

        return deck
