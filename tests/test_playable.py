import unittest
from unittest.mock import Mock

import tests.data as data
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    PlayedCard,
    get_decks_diff,
)


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


class TestPlayedCard(unittest.TestCase):
    def test_equality_case_insensitive(self):
        self.assertEqual(PlayedCard(4, "Lightning Bolt"), PlayedCard(4, "lightning bolt"))

    def test_inequality_different_quantity(self):
        self.assertNotEqual(PlayedCard(4, "Lightning Bolt"), PlayedCard(3, "Lightning Bolt"))

    def test_inequality_different_name(self):
        self.assertNotEqual(PlayedCard(4, "Lightning Bolt"), PlayedCard(4, "Lava Spike"))

    def test_less_than_case_insensitive(self):
        self.assertLess(PlayedCard(1, "Aaa"), PlayedCard(1, "zzz"))

    def test_quantity_parsed_from_string(self):
        pc = PlayedCard("4", "Lightning Bolt")
        self.assertIsInstance(pc.quantity, int)
        self.assertEqual(pc.quantity, 4)


class TestGetDecksDiff(unittest.TestCase):
    def _make_deck(self, main_cards, side_cards=None):
        return PlayableDeck(main_cards, side_cards or [])

    def test_identical_decks_no_diff(self):
        deck = self._make_deck(data.DECK_MAIN, data.DECK_SIDE)
        diff = get_decks_diff(deck, deck)
        self.assertTupleEqual(([], [], [], []), diff)

    def test_main_plus_one_card(self):
        deck1 = self._make_deck(data.DECK_MAIN)
        extra = [PlayedCard(1, "Fake Card")]
        deck2 = self._make_deck(data.DECK_MAIN + extra)
        main_minus, main_plus, side_minus, side_plus = get_decks_diff(deck1, deck2)
        self.assertIn("1 Fake Card", main_plus)
        self.assertEqual(main_minus, [])
        self.assertEqual(side_minus, [])
        self.assertEqual(side_plus, [])

    def test_main_minus_one_card(self):
        deck1 = self._make_deck(data.DECK_MAIN + [PlayedCard(1, "Fake Card")])
        deck2 = self._make_deck(data.DECK_MAIN)
        main_minus, main_plus, _, _ = get_decks_diff(deck1, deck2)
        self.assertIn("1 Fake Card", main_minus)

    def test_side_diff(self):
        deck1 = self._make_deck(data.DECK_MAIN, data.DECK_SIDE)
        deck2 = self._make_deck(data.DECK_MAIN, [PlayedCard(15, "Pyroblast")])
        _, _, side_minus, side_plus = get_decks_diff(deck1, deck2)
        self.assertTrue(len(side_minus) > 0)
        self.assertIn("15 Pyroblast", side_plus)


class TestPlayableDeckIsLegal(unittest.TestCase):
    def test_legal_deck_no_banned_cards(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertTrue(pd.is_legal(["Black Lotus", "Ancestral Recall"]))

    def test_illegal_deck_banned_in_main(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertFalse(pd.is_legal(["Lightning Bolt"]))

    def test_illegal_deck_banned_in_side(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertFalse(pd.is_legal(["Electrickery"]))

    def test_legal_with_empty_banned_list(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertTrue(pd.is_legal([]))


class TestPlayableDeckCanBelongToArchetype(unittest.TestCase):
    def _archetype(self, must_have=None, must_not_have=None):
        archetype = Mock()
        archetype.must_have_cards = must_have or []
        archetype.must_not_have_cards = must_not_have or []
        return archetype

    def test_no_restrictions_always_matches(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertTrue(pd.can_belong_to_archetype(self._archetype()))

    def test_must_have_present(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertTrue(pd.can_belong_to_archetype(self._archetype(must_have=["Lightning Bolt"])))

    def test_must_have_absent(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertFalse(pd.can_belong_to_archetype(self._archetype(must_have=["Black Lotus"])))

    def test_must_not_have_absent(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertTrue(pd.can_belong_to_archetype(self._archetype(must_not_have=["Black Lotus"])))

    def test_must_not_have_present(self):
        pd = PlayableDeck(data.DECK_MAIN, data.DECK_SIDE)
        self.assertFalse(pd.can_belong_to_archetype(self._archetype(must_not_have=["Lightning Bolt"])))


if __name__ == "__main__":
    unittest.main()
