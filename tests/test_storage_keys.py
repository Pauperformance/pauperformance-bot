import unittest

from pauperformance_bot.service.pauperformance.storage.abstract import (
    AbstractStorageService,
)

_DECKSTATS_KEY = "/root/decks/deckstats/99999>7654321>Burn 42.001.Player.txt"
_GOLDFISH_KEY = "/root/decks/mtggoldfish/12345>67890>Faeries 99.042.Alice.txt"
_TWITCH_KEY = "/root/videos/twitch/v123>streamer>en>2023-01-15>Burn 42.001.txt"
_YOUTUBE_KEY = "/root/videos/youtube/abcXYZ>Channel>it>2023-06-01>Faeries 42.001.txt"


class TestStorageKeyParsing(unittest.TestCase):
    def test_deckstats_deck_id(self):
        self.assertEqual(
            AbstractStorageService.get_imported_deckstats_deck_id_from_key(
                _DECKSTATS_KEY
            ),
            "99999",
        )

    def test_deckstats_deck_name_strips_extension(self):
        self.assertEqual(
            AbstractStorageService.get_imported_deckstats_deck_name_from_key(
                _DECKSTATS_KEY
            ),
            "Burn 42.001.Player",
        )

    def test_mtggoldfish_deck_id(self):
        self.assertEqual(
            AbstractStorageService.get_imported_mtggoldfish_deck_id_from_key(
                _GOLDFISH_KEY
            ),
            "12345",
        )

    def test_mtggoldfish_deck_name_strips_extension(self):
        self.assertEqual(
            AbstractStorageService.get_imported_mtggoldfish_deck_name_from_key(
                _GOLDFISH_KEY
            ),
            "Faeries 99.042.Alice",
        )

    def test_twitch_video_id(self):
        self.assertEqual(
            AbstractStorageService.get_imported_twitch_video_id_from_key(_TWITCH_KEY),
            "v123",
        )

    def test_twitch_video_full_name(self):
        self.assertEqual(
            AbstractStorageService.get_imported_twitch_video(_TWITCH_KEY),
            "v123>streamer>en>2023-01-15>Burn 42.001",
        )

    def test_youtube_video_id(self):
        self.assertEqual(
            AbstractStorageService.get_imported_youtube_video_id_from_key(_YOUTUBE_KEY),
            "abcXYZ",
        )

    def test_youtube_video_full_name(self):
        self.assertEqual(
            AbstractStorageService.get_imported_youtube_video(_YOUTUBE_KEY),
            "abcXYZ>Channel>it>2023-06-01>Faeries 42.001",
        )


if __name__ == "__main__":
    unittest.main()
