import unittest

from pauperformance_bot.entity.deck.playable import PlayedCard
from pauperformance_bot.util.decklist_parser import MtgoDeckListParser

_SIXTY_FORESTS = ["60 Forest"]
_SIXTY_FORESTS_AND_SIDE = ["60 Forest", "", "15 Island"]


class TestMtgoDeckListParser(unittest.TestCase):
    def setUp(self):
        self.parser = MtgoDeckListParser()

    def test_parse_with_sideboard(self):
        deck = self.parser.parse_lines(_SIXTY_FORESTS_AND_SIDE[:])
        self.assertEqual(deck.len_mainboard, 60)
        self.assertEqual(deck.len_sideboard, 15)

    def test_parse_without_sideboard(self):
        deck = self.parser.parse_lines(_SIXTY_FORESTS[:])
        self.assertEqual(deck.len_mainboard, 60)
        self.assertEqual(deck.len_sideboard, 0)

    def test_parse_multiword_card_name(self):
        lines = ["4 Burning-Tree Emissary", "56 Forest", "", "15 Relic of Progenitus"]
        deck = self.parser.parse_lines(lines)
        names = {c.card_name for c in deck.mainboard}
        self.assertIn("Burning-Tree Emissary", names)

    def test_parse_sorts_mainboard_by_name(self):
        lines = ["4 Zzz Card", "4 Aaa Card", "4 Lightning Bolt", "48 Forest"]
        deck = self.parser.parse_lines(lines)
        names = [c.card_name for c in deck.mainboard]
        self.assertEqual(names, sorted(names))

    def test_parse_sorts_sideboard_by_name(self):
        lines = ["60 Forest", "", "4 Pyroblast", "4 Hydroblast", "4 Gorilla Shaman", "3 Relic of Progenitus"]
        deck = self.parser.parse_lines(lines)
        names = [c.card_name for c in deck.sideboard]
        self.assertEqual(names, sorted(names))

    def test_parse_quantity_is_int(self):
        deck = self.parser.parse_lines(_SIXTY_FORESTS[:])
        self.assertIsInstance(deck.mainboard[0].quantity, int)
        self.assertEqual(deck.mainboard[0].quantity, 60)

    def test_parse_card_equality(self):
        lines = ["4 Lightning Bolt", "56 Forest"]
        deck = self.parser.parse_lines(lines)
        self.assertIn(PlayedCard(4, "Lightning Bolt"), deck.mainboard)


if __name__ == "__main__":
    unittest.main()
