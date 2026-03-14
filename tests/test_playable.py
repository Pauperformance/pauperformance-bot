import unittest

import tests.data as data
from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard


class TestPlayableDeck(unittest.TestCase):
    def test_playable_deck_with_no_sideboard(self) -> None:
        pd: PlayableDeck = PlayableDeck(data.DECK_MAIN, [])

        self.assertIsNotNone(pd)
        self.assertListEqual(data.DECK_MAIN, pd.mainboard)
        self.assertEqual(len(pd.sideboard), 0)

    def test_playable_deck_with_more_than_sixty_main(self) -> None:
        main_deck: list[PlayedCard] = data.DECK_MAIN + [PlayedCard(4, "Fake Card")]

        pd: PlayableDeck = PlayableDeck(main_deck, [])

        self.assertIsNotNone(pd)
        self.assertListEqual(main_deck, pd.mainboard)
        self.assertEqual(len(pd.sideboard), 0)

    def test_playable_deck_with_less_than_sixty_main(self) -> None:
        main_deck: list[PlayedCard] = data.DECK_MAIN[:-1]

        with self.assertRaises(ValueError):
            PlayableDeck(main_deck, [])

    def test_playable_deck_with_more_than_fifteen_side(self) -> None:
        side_deck: list[PlayedCard] = data.DECK_SIDE + [PlayedCard(4, "Fake Card")]

        with self.assertRaises(ValueError):
            PlayableDeck(data.DECK_MAIN, side_deck)

    def test_playable_deck(self) -> None:
        pd: PlayableDeck = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)

        self.assertListEqual(data.DECK_MAIN, pd.mainboard)
        self.assertListEqual(data.DECK_SIDE, pd.sideboard)

    def test_playable_deck_with_less_than_fifteen_side(self) -> None:
        pd: PlayableDeck = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE[:-1])

        self.assertListEqual(data.DECK_MAIN, pd.mainboard)
        self.assertListEqual(data.DECK_SIDE[:-1], pd.sideboard)


if __name__ == "__main__":
    unittest.main()
