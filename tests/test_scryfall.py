import json
import os
import pickle
import tempfile
import unittest
from unittest import mock

import requests

from pauperformance_bot.entity.api.archetype import ArchetypeCard
from pauperformance_bot.exceptions import CardNotFoundException
from pauperformance_bot.service.mtg.scryfall import ScryfallService


def _mock_response(data):
    m = mock.MagicMock()
    m.content = json.dumps(data).encode()
    return m


class TestScryfallServiceGetSets(unittest.TestCase):
    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_returns_parsed_json(self, mock_req):
        data = {"object": "list", "data": [{"id": "abc", "name": "Alpha"}]}
        mock_req.return_value = _mock_response(data)
        svc = ScryfallService()
        result = svc.get_sets()
        self.assertEqual(result["data"][0]["name"], "Alpha")

    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_calls_sets_endpoint(self, mock_req):
        mock_req.return_value = _mock_response({})
        svc = ScryfallService(endpoint="https://test.example.com")
        svc.get_sets()
        url_called = mock_req.call_args[0][1]
        self.assertEqual(url_called, "https://test.example.com/sets")


class TestScryfallServiceGetCardNamed(unittest.TestCase):
    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_cache_miss_returns_card(self, mock_req):
        card_data = {
            "name": "Lightning Bolt",
            "scryfall_uri": "https://scryfall.com/card/lea/161?utm_source=api",
            "image_uris": {"normal": "https://img.scryfall.com/bolt.jpg"},
        }
        mock_req.return_value = _mock_response(card_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = ScryfallService()
            result = svc.get_card_named("Lightning Bolt", cards_cache_dir=tmpdir)
            self.assertEqual(result["name"], "Lightning Bolt")

    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_cache_miss_writes_cache_file(self, mock_req):
        card_data = {"name": "Counterspell", "scryfall_uri": "https://x"}
        mock_req.return_value = _mock_response(card_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = ScryfallService()
            svc.get_card_named("Counterspell", cards_cache_dir=tmpdir)
            cache_file = os.path.join(tmpdir, "Counterspell.pkl")
            self.assertTrue(os.path.exists(cache_file))

    def test_cache_hit_returns_without_http(self):
        card_data = {"name": "Brainstorm", "scryfall_uri": "https://x"}
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "Brainstorm.pkl")
            with open(cache_path, "wb") as f:
                pickle.dump(card_data, f)
            svc = ScryfallService()
            result = svc.get_card_named("Brainstorm", cards_cache_dir=tmpdir)
            self.assertEqual(result["name"], "Brainstorm")

    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_404_raises_card_not_found(self, mock_req):
        resp_mock = mock.MagicMock(status_code=404)
        exc = requests.exceptions.HTTPError(response=resp_mock)
        exc.response = resp_mock
        mock_req.side_effect = exc
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = ScryfallService()
            with self.assertRaises(CardNotFoundException):
                svc.get_card_named("Nonexistent Card XYZ", cards_cache_dir=tmpdir)

    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_non_404_http_error_reraises(self, mock_req):
        resp_mock = mock.MagicMock(status_code=500)
        exc = requests.exceptions.HTTPError(response=resp_mock)
        exc.response = resp_mock
        mock_req.side_effect = exc
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = ScryfallService()
            with self.assertRaises(requests.exceptions.HTTPError):
                svc.get_card_named("Some Card", cards_cache_dir=tmpdir)


class TestScryfallServiceSearchCards(unittest.TestCase):
    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_single_page(self, mock_req):
        response_data = {"data": [{"name": "Lightning Bolt"}], "has_more": False}
        mock_req.return_value = _mock_response(response_data)
        svc = ScryfallService()
        result = svc.search_cards("type:instant")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Lightning Bolt")

    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_multi_page_concatenates_results(self, mock_req):
        page1 = {
            "data": [{"name": "A"}],
            "has_more": True,
            "next_page": "https://api.scryfall.com/cards/search?page=2",
        }
        page2 = {"data": [{"name": "B"}], "has_more": False}
        mock_req.side_effect = [_mock_response(page1), _mock_response(page2)]
        svc = ScryfallService()
        result = svc.search_cards("type:land")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "A")
        self.assertEqual(result[1]["name"], "B")

    @mock.patch("pauperformance_bot.service.mtg.scryfall.execute_http_request")
    def test_not_found_returns_empty(self, mock_req):
        not_found = mock.MagicMock(
            status_code=404,
            content=json.dumps({"code": "not_found"}).encode(),
        )
        exc = requests.exceptions.HTTPError(response=not_found)
        exc.response = not_found
        mock_req.side_effect = exc
        svc = ScryfallService()
        result = svc.search_cards("type:nonexistent_xyzzy")
        self.assertEqual(result, {})


class TestScryfallServiceConvenienceMethods(unittest.TestCase):
    @mock.patch.object(
        ScryfallService, "search_cards", return_value=[{"name": "Forest"}]
    )
    def test_get_legal_lands_delegates(self, mock_search):
        svc = ScryfallService()
        result = svc.get_legal_lands()
        mock_search.assert_called_once_with("type:land legal:pauper")
        self.assertEqual(len(result), 1)

    @mock.patch.object(ScryfallService, "search_cards", return_value=[])
    def test_get_legal_artifact_lands_delegates(self, mock_search):
        svc = ScryfallService()
        svc.get_legal_artifact_lands()
        mock_search.assert_called_once_with("(type:artifact type:land) legal:pauper")

    @mock.patch.object(ScryfallService, "search_cards", return_value=[])
    def test_get_banned_cards_delegates(self, mock_search):
        svc = ScryfallService()
        svc.get_banned_cards()
        mock_search.assert_called_once_with("banned:pauper")


class TestScryfallServiceGetArtistGalleryUrl(unittest.TestCase):
    def test_url_contains_artist_name(self):
        svc = ScryfallService(website_url="https://scryfall.com")
        url = svc.get_artist_gallery_search_url("Rebecca Guay")
        self.assertIn("scryfall.com", url)
        self.assertIn("Rebecca", url)

    def test_url_has_grid_and_order_params(self):
        svc = ScryfallService(website_url="https://scryfall.com")
        url = svc.get_artist_gallery_search_url("John Avon")
        self.assertIn("unique=art", url)
        self.assertIn("as=grid", url)
        self.assertIn("order=name", url)


class TestScryfallServiceGetArchetypeCards(unittest.TestCase):
    def _fake_card(self, name):
        return {
            "image_uris": {"normal": f"https://img.scryfall.com/{name}.jpg?v=1"},
            "scryfall_uri": f"https://scryfall.com/card/x/{name}?utm_source=api",
        }

    @mock.patch.object(ScryfallService, "get_card_named")
    def test_returns_archetype_card_list(self, mock_get):
        mock_get.side_effect = lambda name, **kw: self._fake_card(name)
        svc = ScryfallService()
        result = svc.get_archetype_cards(["Lightning Bolt"])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ArchetypeCard)
        self.assertEqual(result[0].name, "Lightning Bolt")

    @mock.patch.object(ScryfallService, "get_card_named")
    def test_image_query_string_stripped(self, mock_get):
        mock_get.side_effect = lambda name, **kw: self._fake_card(name)
        svc = ScryfallService()
        result = svc.get_archetype_cards(["Lightning Bolt"])
        self.assertNotIn("?", result[0].preview)

    @mock.patch.object(ScryfallService, "get_card_named")
    def test_utm_source_stripped_from_link(self, mock_get):
        mock_get.side_effect = lambda name, **kw: self._fake_card(name)
        svc = ScryfallService()
        result = svc.get_archetype_cards(["Lightning Bolt"])
        self.assertNotIn("utm_source", result[0].link)

    @mock.patch.object(ScryfallService, "get_card_named")
    def test_dfc_uses_first_face_image(self, mock_get):
        mock_get.return_value = {
            "card_faces": [
                {"image_uris": {"normal": "https://img.scryfall.com/delver.jpg"}}
            ],
            "scryfall_uri": "https://scryfall.com/card/b?utm_source=api",
        }
        svc = ScryfallService()
        result = svc.get_archetype_cards(["Delver of Secrets"])
        self.assertEqual(result[0].preview, "https://img.scryfall.com/delver.jpg")

    @mock.patch.object(ScryfallService, "get_card_named")
    def test_cards_sorted_alphabetically(self, mock_get):
        mock_get.side_effect = lambda name, **kw: self._fake_card(name)
        svc = ScryfallService()
        result = svc.get_archetype_cards(["Swamp", "Lightning Bolt", "Forest"])
        names = [c.name for c in result]
        self.assertEqual(names, sorted(names))


if __name__ == "__main__":
    unittest.main()
