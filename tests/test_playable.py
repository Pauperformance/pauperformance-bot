import unittest

import tests.data as data
from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard


class TestPlayableDeck(unittest.TestCase):
    def test_playable_deck_with_no_sideboard(self):

        pd = PlayableDeck(data.DECK_MAIN, [])

        self.assertIsNotNone(pd)
        self.assertListEqual(data.DECK_MAIN, pd.mainboard)
        self.assertEqual(len(pd.sideboard), 0)

    def test_playable_deck_with_more_than_sixty_main(self):
        main_deck = data.DECK_MAIN + [PlayedCard(4, "Fake Card")]

        pd = PlayableDeck(main_deck, [])

        self.assertIsNotNone(pd)
        self.assertListEqual(main_deck, pd.mainboard)
        self.assertEqual(len(pd.sideboard), 0)

    def test_playable_deck_with_less_than_sixty_main(self):
        main_deck = data.DECK_MAIN[:-1]

        with self.assertRaises(ValueError):
            PlayableDeck(main_deck, [])

    def test_playable_deck_with_more_than_fifteen_side(self):
        side_deck = data.DECK_SIDE + [PlayedCard(4, "Fake Card")]

        with self.assertRaises(ValueError):
            PlayableDeck(data.DECK_MAIN, side_deck)

    def test_playable_deck(self):

        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)

        self.assertListEqual(data.DECK_MAIN, pd.mainboard)
        self.assertListEqual(data.DECK_SIDE, pd.sideboard)

    def test_playable_deck_with_less_than_fifteen_side(self):

        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE[:-1])

        self.assertListEqual(data.DECK_MAIN, pd.mainboard)
        self.assertListEqual(data.DECK_SIDE[:-1], pd.sideboard)


if __name__ == "__main__":
    unittest.main()
