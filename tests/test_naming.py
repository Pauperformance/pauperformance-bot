import unittest

from pauperformance_bot.util.naming import (
    is_valid_p12e_deck_name,
    is_valid_p12e_deckstats_name,
)


class TestIsValidP12eDeckstatsName(unittest.TestCase):
    def test_valid_single_word_archetype(self):
        self.assertTrue(is_valid_p12e_deckstats_name("Burn 123.001"))

    def test_valid_multiword_archetype(self):
        self.assertTrue(is_valid_p12e_deckstats_name("Mono Blue Faeries 456.042"))

    def test_invalid_empty_string(self):
        self.assertFalse(is_valid_p12e_deckstats_name(""))

    def test_invalid_no_archetype(self):
        self.assertFalse(is_valid_p12e_deckstats_name("123.001"))

    def test_invalid_no_dot(self):
        self.assertFalse(is_valid_p12e_deckstats_name("Burn 123001"))

    def test_invalid_two_dots(self):
        self.assertFalse(is_valid_p12e_deckstats_name("Burn 123.001.extra"))

    def test_invalid_deck_number_too_short(self):
        self.assertFalse(is_valid_p12e_deckstats_name("Burn 123.01"))

    def test_invalid_deck_number_too_long(self):
        self.assertFalse(is_valid_p12e_deckstats_name("Burn 123.0001"))

    def test_valid_deck_number_exactly_three(self):
        self.assertTrue(is_valid_p12e_deckstats_name("Affinity 99.000"))
        self.assertTrue(is_valid_p12e_deckstats_name("Affinity 99.999"))


class TestIsValidP12eDeckName(unittest.TestCase):
    def test_valid_single_word_archetype(self):
        self.assertTrue(is_valid_p12e_deck_name("Burn 123.001.PlayerName"))

    def test_valid_multiword_archetype(self):
        self.assertTrue(is_valid_p12e_deck_name("Mono Blue Faeries 456.042.Alice"))

    def test_invalid_empty_string(self):
        self.assertFalse(is_valid_p12e_deck_name(""))

    def test_invalid_no_archetype(self):
        self.assertFalse(is_valid_p12e_deck_name("123.001.Player"))

    def test_invalid_one_dot(self):
        self.assertFalse(is_valid_p12e_deck_name("Burn 123.001"))

    def test_invalid_three_dots(self):
        self.assertFalse(is_valid_p12e_deck_name("Burn 123.001.Player.extra"))

    def test_invalid_deck_number_too_short(self):
        self.assertFalse(is_valid_p12e_deck_name("Burn 123.01.Player"))

    def test_invalid_deck_number_too_long(self):
        self.assertFalse(is_valid_p12e_deck_name("Burn 123.0001.Player"))

    def test_player_id_can_be_empty(self):
        self.assertTrue(is_valid_p12e_deck_name("Burn 123.001."))

    def test_valid_deck_number_exactly_three(self):
        self.assertTrue(is_valid_p12e_deck_name("Affinity 99.000.Player"))
        self.assertTrue(is_valid_p12e_deck_name("Affinity 99.999.Player"))


if __name__ == "__main__":
    unittest.main()
