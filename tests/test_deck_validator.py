import unittest
from pauperformance_bot.entity.deck.playable import PlayedCard

from pauperformance_bot.util.validate import PlayableDeckValidator


DECK_MAIN = [
    PlayedCard(4, "Thermo-Alchemist"),
    PlayedCard(4, "Voldaren Epicure"),
    PlayedCard(4, "Needle Drop"),
    PlayedCard(4, "Searing Blaze"),
    PlayedCard(4, "Lightning Bolt"),
    PlayedCard(4, "Fireblast"),
    PlayedCard(3, "Flame Rift"),
    PlayedCard(4, "Skewer the Critics"),
    PlayedCard(4, "Rift Bolt"),
    PlayedCard(4, "Lava Spike"),
    PlayedCard(4, "Chain Lightning"),
    PlayedCard(1, "Forgotten Cave"),
    PlayedCard(16, "Mountain"),
]
DECK_SIDE = [
    PlayedCard(2, "Molten Rain"),
    PlayedCard(2, "Martyr of Ashes"),
    PlayedCard(3, "Electrickery"),
    PlayedCard(4, "Smash to Smithereens"),
    PlayedCard(4, "Keldon Marauders"),
]


class TestPlayableDeckValidator(unittest.TestCase):

    def test_deck_is_valid_with_no_sideboard(self):

        pdv = PlayableDeckValidator([], [])
        


