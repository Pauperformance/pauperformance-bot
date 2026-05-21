import unittest

from pauperformance_bot.service.pauperformance.storage.abstract import (
    AbstractStorageService,
)


class _ConcreteStorage(AbstractStorageService):
    @property
    def _root(self):
        return "/storage"

    @property
    def _dir_separator(self):
        return "/"

    def _list_files(self, path, cursor=None):
        return []

    def create_file(self, name, content=""):
        pass

    def get_file(self, name):
        pass

    def list_imported_deckstats_deck_ids(self):
        return []

    def list_imported_deckstats_deck_names(self):
        return []

    def list_imported_mtggoldfish_deck_ids(self):
        return []

    def list_imported_mtggoldfish_deck_names(self):
        return []

    def list_imported_youtube_videos(self):
        return []

    def list_imported_youtube_videos_ids(self):
        return []

    def delete_deck_by_name(self, deck_name):
        pass


class TestAbstractStorageProperties(unittest.TestCase):
    def setUp(self):
        self.svc = _ConcreteStorage()

    def test_decks_path(self):
        self.assertEqual(self.svc.decks_path, "/storage/decks")

    def test_deckstats_deck_path(self):
        self.assertIn("deckstats", self.svc.deckstats_deck_path)

    def test_mtggoldfish_deck_path(self):
        self.assertIn("mtggoldfish", self.svc.mtggoldfish_deck_path)

    def test_videos_path(self):
        self.assertEqual(self.svc.videos_path, "/storage/videos")

    def test_youtube_video_path(self):
        self.assertIn("youtube", self.svc.youtube_video_path)


class TestAbstractStorageKeyBuilders(unittest.TestCase):
    def setUp(self):
        self.svc = _ConcreteStorage()

    def test_get_imported_deckstats_deck_key(self):
        key = self.svc.get_imported_deckstats_deck_key(
            "99999", "7654321", "Burn 42.001.Player"
        )
        self.assertIn("99999", key)
        self.assertIn("7654321", key)
        self.assertIn("Burn 42.001.Player.txt", key)

    def test_get_imported_mtggoldfish_deck_key(self):
        key = self.svc.get_imported_mtggoldfish_deck_key(
            "12345", "67890", "Faeries 99.042.Alice"
        )
        self.assertIn("12345", key)
        self.assertIn("Faeries 99.042.Alice.txt", key)

    def test_get_imported_youtube_video_key(self):
        key = self.svc.get_imported_youtube_video_key(
            "abcXYZ", "Channel", "it", "2023-06-01", "Faeries 42.001"
        )
        self.assertIn("abcXYZ", key)
        self.assertIn("Channel", key)
        self.assertIn("Faeries 42.001.txt", key)


if __name__ == "__main__":
    unittest.main()
