import unittest

from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.exceptions import UnsupportedLanguage


class TestGetLanguageFlag(unittest.TestCase):
    def test_italian_long(self):
        self.assertEqual(get_language_flag("ita"), "🇮🇹")

    def test_italian_short(self):
        self.assertEqual(get_language_flag("it"), "🇮🇹")

    def test_english_long(self):
        self.assertEqual(get_language_flag("eng"), "🇬🇧")

    def test_english_short(self):
        self.assertEqual(get_language_flag("en"), "🇬🇧")

    def test_case_insensitive(self):
        self.assertEqual(get_language_flag("ITA"), "🇮🇹")
        self.assertEqual(get_language_flag("ENG"), "🇬🇧")
        self.assertEqual(get_language_flag("IT"), "🇮🇹")

    def test_unknown_language_raises(self):
        with self.assertRaises(UnsupportedLanguage):
            get_language_flag("fr")

    def test_empty_raises(self):
        with self.assertRaises(UnsupportedLanguage):
            get_language_flag("")


if __name__ == "__main__":
    unittest.main()
