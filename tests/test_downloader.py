import unittest
from unittest import mock

from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    PlayedCard,
    get_decks_diff,
)
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader
from pauperformance_bot.service.mtg.downloader.mtgdecks import MtgdecksDeckDownloader

EXPECTED_DECK_AETHERHUB_MAIN = [
    PlayedCard(3, "Thoughtcast"),
    PlayedCard(2, "Krark-Clan Shaman"),
    PlayedCard(3, "Great Furnace"),
    PlayedCard(3, "Seat of the Synod"),
    PlayedCard(3, "Vault of Whispers"),
    PlayedCard(1, "Reckoner's Bargain"),
    PlayedCard(4, "Deadly Dispute"),
    PlayedCard(4, "Galvanic Blast"),
    PlayedCard(2, "Experimental Synthesizer"),
    PlayedCard(4, "Drossforge Bridge"),
    PlayedCard(3, "Mistvault Bridge"),
    PlayedCard(3, "Silverbluff Bridge"),
    PlayedCard(4, "Ichor Wellspring"),
    PlayedCard(2, "Blood Fountain"),
    PlayedCard(2, "Frogmite"),
    PlayedCard(4, "Myr Enforcer"),
    PlayedCard(2, "Kenku Artificer"),
    PlayedCard(1, "Gearseeker Serpent"),
    PlayedCard(1, "Cast Down"),
    PlayedCard(2, "Metallic Rebuke"),
    PlayedCard(4, "Chromatic Star"),
    PlayedCard(1, "Makeshift Munitions"),
    PlayedCard(1, "Nihil Spellbomb"),
    PlayedCard(1, "Aether Spellbomb"),
]
EXPECTED_DECK_AETHERHUB_SIDE = [
    PlayedCard(2, "Gorilla Shaman"),
    PlayedCard(3, "Hydroblast"),
    PlayedCard(4, "Pyroblast"),
    PlayedCard(2, "Negate"),
    PlayedCard(2, "Chainer's Edict"),
    PlayedCard(1, "Electrickery"),
    PlayedCard(1, "Makeshift Munitions"),
]
EXPECTED_DECK_TAPPEDOUT_MAIN = [
    PlayedCard(4, "Chromatic Star"),
    PlayedCard(4, "Drossforge Bridge"),
    PlayedCard(1, "Duress"),
    PlayedCard(2, "Faithless Looting"),
    PlayedCard(4, "First Day of Class"),
    PlayedCard(1, "Flamewave Invoker"),
    PlayedCard(1, "Forgotten Cave"),
    PlayedCard(4, "Goblin Matron"),
    PlayedCard(1, "Goblin Sledder"),
    PlayedCard(2, "Great Furnace"),
    PlayedCard(3, "Ichor Wellspring"),
    PlayedCard(2, "Makeshift Munitions"),
    PlayedCard(1, "Masked Vandal"),
    PlayedCard(1, "Mogg War Marshal"),
    PlayedCard(4, "Mountain"),
    PlayedCard(4, "Putrid Goblin"),
    PlayedCard(2, "Rakdos Carnarium"),
    PlayedCard(4, "Reckoner's Bargain"),
    PlayedCard(1, "Shred Memory"),
    PlayedCard(4, "Skirk Prospector"),
    PlayedCard(4, "Swamp"),
    PlayedCard(4, "Unearth"),
    PlayedCard(2, "Vault of Whispers"),
]
EXPECTED_DECK_TAPPEDOUT_SIDE = [
    PlayedCard(2, "Abrade"),
    PlayedCard(2, "Cuombajj Witches"),
    PlayedCard(2, "Duress"),
    PlayedCard(1, "Gorilla Shaman"),
    PlayedCard(2, "Introduction to Prophecy"),
    PlayedCard(1, "Krark-Clan Shaman"),
    PlayedCard(1, "Nameless Inversion"),
    PlayedCard(4, "Pyroblast"),
]
EXPECTED_DECK_MTGTOP8_MAIN = [
    PlayedCard(2, "River Boa"),
    PlayedCard(2, "Silhana Ledgewalker"),
    PlayedCard(3, "Vault Skirge"),
    PlayedCard(3, "Quirion Ranger"),
    PlayedCard(3, "Skarrgan Pit-Skulk"),
    PlayedCard(4, "Nest Invader"),
    PlayedCard(4, "Burning-Tree Emissary"),
    PlayedCard(4, "Nettle Sentinel"),
    PlayedCard(3, "Hunger of the Howlpack"),
    PlayedCard(4, "Vines of Vastwood"),
    PlayedCard(4, "Savage Swipe"),
    PlayedCard(3, "Elephant Guide"),
    PlayedCard(4, "Rancor"),
    PlayedCard(17, "Forest"),
]
EXPECTED_DECK_MTGTOP8_SIDE = [
    PlayedCard(2, "Weather the Storm"),
    PlayedCard(2, "Epic Confrontation"),
    PlayedCard(2, "Relic of Progenitus"),
    PlayedCard(2, "Viridian Longbow"),
    PlayedCard(3, "Gut Shot"),
    PlayedCard(4, "Gleeful Sabotage"),
]
EXPECTED_DECK_MTGDECKS_MAIN = [
    PlayedCard(4, "Thermo-Alchemist"),
    PlayedCard(4, "Voldaren Epicure"),
    PlayedCard(4, "Needle Drop"),
    PlayedCard(4, "Searing Blaze"),
    PlayedCard(4, "Lightning Bolt"),
    PlayedCard(4, "Fireblast"),
    PlayedCard(3, "Flame Rift"),
    PlayedCard(4, "Skewer the Critics"),
    PlayedCard(4, "Rift Bolt"),
    PlayedCard(4, "Lava Spike"),
    PlayedCard(4, "Chain Lightning"),
    PlayedCard(1, "Forgotten Cave"),
    PlayedCard(16, "Mountain"),
]
EXPECTED_DECK_MTGDECKS_SIDE = [
    PlayedCard(2, "Molten Rain"),
    PlayedCard(2, "Martyr of Ashes"),
    PlayedCard(3, "Electrickery"),
    PlayedCard(4, "Smash to Smithereens"),
    PlayedCard(4, "Keldon Marauders"),
]


class TestMtgoDownloader(unittest.TestCase):
    def _read_mock_data(self, filename):
        with open(filename) as fd:
            return fd.read()

    def _validate_result(self, expected, res):
        self.assertIsNotNone(res, "Should return a deck")
        diff = get_decks_diff(expected, res)
        self.assertTupleEqual(([], [], [], []), diff, "Should not have any difference")

    @mock.patch("pauperformance_bot.util.request.execute_http_request")
    def test_mtgo_downloader_aetherhub(self, mock_ehr):
        mock_ehr.return_value = self._read_mock_data(
            "tests/mock_data/aetherhub_deck.txt"
        )
        expected_deck = PlayableDeck(
            EXPECTED_DECK_AETHERHUB_MAIN, EXPECTED_DECK_AETHERHUB_SIDE
        )
        downloader = MtgoDeckDownloader(
            "https://aetherhub.com/Deck/MtgoDeckExport/883786"
        )

        res = downloader.download()

        self._validate_result(expected_deck, res)

    @mock.patch("pauperformance_bot.util.request.execute_http_request")
    def test_mtgo_downloader_mtgtop8(self, mock_ehr):
        mock_ehr.return_value = self._read_mock_data("tests/mock_data/mtgtop8_deck.txt")
        expected_deck = PlayableDeck(
            EXPECTED_DECK_MTGTOP8_MAIN, EXPECTED_DECK_MTGTOP8_SIDE
        )
        downloader = MtgoDeckDownloader("https://www.mtgtop8.com/mtgo?d=473002")

        res = downloader.download()

        self._validate_result(expected_deck, res)

    @mock.patch("pauperformance_bot.util.request.execute_http_request")
    def test_mtgo_downloader_tappedout(self, mock_ehr):
        mock_ehr.return_value = self._read_mock_data(
            "tests/mock_data/tappedout_deck.txt"
        )
        expected_deck = PlayableDeck(
            EXPECTED_DECK_TAPPEDOUT_MAIN, EXPECTED_DECK_TAPPEDOUT_SIDE
        )
        downloader = MtgoDeckDownloader(
            "https://tappedout.net/mtg-decks/gobliny-combo/?fmt=dek&cb=1653244312"
        )

        res = downloader.download()

        self._validate_result(expected_deck, res)

    def test_downloader_mtgdeck(self):
        expected_deck = PlayableDeck(
            EXPECTED_DECK_MTGDECKS_MAIN, EXPECTED_DECK_MTGDECKS_SIDE
        )
        downloader = MtgdecksDeckDownloader(
            "https://mtgdecks.net/Pauper/burn-decklist-by-thormyn-1380435/txt"
        )

        res = downloader.download()

        self._validate_result(expected_deck, res)


if __name__ == "__main__":
    unittest.main()
