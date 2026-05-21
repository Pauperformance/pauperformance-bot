import io
import json
import os
import tempfile
import unittest
import zipfile
from unittest import mock

from pauperformance_bot.service.pauperformance.storage.abstract import (
    AbstractStorageService,
)
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.service.pauperformance.storage.local import LocalStorageService

_SAMPLE_FILES = {
    "abc>channel>en>2024-01-01>Affinity.txt": {"id": "abc", "language": "en"},
    "xyz>channel>it>2024-02-15>Burn.txt": {"id": "xyz", "language": "it"},
}


def _make_zip_bytes(sample_files, folder_name="youtube"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in sample_files.items():
            zf.writestr(f"{folder_name}/{name}", json.dumps(content))
    return buf.getvalue()


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

    def update_file(self, name, content=""):
        pass

    def get_file(self, name):
        pass

    def get_folder(self, path):
        return {}

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


class TestLocalStorageGetFolder(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        for name, content in _SAMPLE_FILES.items():
            with open(os.path.join(self._tmpdir.name, name), "w") as f:
                json.dump(content, f)
        self.svc = LocalStorageService(root_dir=self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_returns_dict(self):
        result = self.svc.get_folder(self._tmpdir.name)
        self.assertIsInstance(result, dict)

    def test_keys_are_bare_filenames(self):
        result = self.svc.get_folder(self._tmpdir.name)
        self.assertEqual(set(result.keys()), set(_SAMPLE_FILES.keys()))

    def test_values_are_parsed_dicts(self):
        result = self.svc.get_folder(self._tmpdir.name)
        for value in result.values():
            self.assertIsInstance(value, dict)

    def test_content_matches_written_data(self):
        result = self.svc.get_folder(self._tmpdir.name)
        for name, expected in _SAMPLE_FILES.items():
            self.assertEqual(result[name], expected)


class TestDropboxServiceGetFolder(unittest.TestCase):
    @mock.patch(
        "pauperformance_bot.service.pauperformance.storage.dropbox_.OfficialDropbox"
    )
    def _make_svc(self, mock_dbx_cls, zip_bytes=None):
        mock_resp = mock.MagicMock()
        mock_resp.content = zip_bytes or _make_zip_bytes(_SAMPLE_FILES)
        mock_dbx_cls.return_value.files_download_zip.return_value = (None, mock_resp)
        svc = DropboxService(
            root_dir="/myr",
            refresh_token="tok",
            app_key="key",
            app_secret="secret",
        )
        svc._service.files_download_zip.return_value = (None, mock_resp)
        return svc

    def test_returns_dict(self):
        result = self._make_svc().get_folder("/myr/videos/youtube")
        self.assertIsInstance(result, dict)

    def test_keys_carry_folder_prefix(self):
        result = self._make_svc().get_folder("/myr/videos/youtube")
        for key in result.keys():
            self.assertIn("/", key)

    def test_values_are_parsed_dicts(self):
        result = self._make_svc().get_folder("/myr/videos/youtube")
        for value in result.values():
            self.assertIsInstance(value, dict)

    def test_bare_filenames_match_sample(self):
        result = self._make_svc().get_folder("/myr/videos/youtube")
        bare = {k.split("/")[-1] for k in result.keys()}
        self.assertEqual(bare, set(_SAMPLE_FILES.keys()))


class TestGetFolderConsistency(unittest.TestCase):
    """Both backends must yield identical content after key normalisation."""

    def _local_result(self):
        tmpdir = tempfile.mkdtemp()
        for name, content in _SAMPLE_FILES.items():
            with open(os.path.join(tmpdir, name), "w") as f:
                json.dump(content, f)
        svc = LocalStorageService(root_dir=tmpdir)
        result = svc.get_folder(tmpdir)
        import shutil

        shutil.rmtree(tmpdir)
        return result

    @mock.patch(
        "pauperformance_bot.service.pauperformance.storage.dropbox_.OfficialDropbox"
    )
    def _dropbox_result(self, mock_dbx_cls):
        mock_resp = mock.MagicMock()
        mock_resp.content = _make_zip_bytes(_SAMPLE_FILES)
        mock_dbx_cls.return_value.files_download_zip.return_value = (None, mock_resp)
        svc = DropboxService(
            root_dir="/myr",
            refresh_token="tok",
            app_key="key",
            app_secret="secret",
        )
        svc._service.files_download_zip.return_value = (None, mock_resp)
        return svc.get_folder("/myr/videos/youtube")

    def test_normalised_dicts_are_equal(self):
        local = {k.split("/")[-1]: v for k, v in self._local_result().items()}
        dropbox = {k.split("/")[-1]: v for k, v in self._dropbox_result().items()}
        self.assertEqual(local, dropbox)


if __name__ == "__main__":
    unittest.main()
