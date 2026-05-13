import unittest

from pauperformance_bot.entity.academy_video import AcademyVideo
from pauperformance_bot.entity.api.archetype import Archetype, ArchetypeCard
from pauperformance_bot.entity.api.creator import CreatorSheet
from pauperformance_bot.entity.api.deck import Deck, MTGGoldfishTournamentDeck
from pauperformance_bot.entity.api.miscellanea import (
    Changelog,
    DPLDeck,
    DPLMeta,
    Metagame,
    MetaShare,
    Newspauper,
)
from pauperformance_bot.entity.api.tournament import Tournament
from pauperformance_bot.entity.api.video import Video
from pauperformance_bot.entity.config.archetype import ChangelogEntry


def _make_archetype(**overrides):
    kwargs = dict(
        name="Burn",
        aliases=[],
        family=None,
        dominant_mana=["R"],
        game_type=["aggro"],
        description="Fast red deck.",
        must_have_cards=[],
        must_not_have_cards=[],
        reference_decks=[],
        resource_sideboard=None,
        resources_discord=[],
        resources=[],
        staples=[],
        frequent=[],
    )
    kwargs.update(overrides)
    return Archetype(**kwargs)


class TestArchetypeCard(unittest.TestCase):
    def test_creation(self):
        card = ArchetypeCard(
            name="Lightning Bolt",
            link="https://scryfall.com/card/a",
            preview="https://img.scryfall.com/a",
        )
        self.assertEqual(card.name, "Lightning Bolt")
        self.assertEqual(card.link, "https://scryfall.com/card/a")

    def test_hash_based_on_name(self):
        c1 = ArchetypeCard(name="Lightning Bolt", link="url1", preview="p1")
        c2 = ArchetypeCard(name="Lightning Bolt", link="url2", preview="p2")
        self.assertEqual(hash(c1), hash(c2))

    def test_repr_and_str(self):
        card = ArchetypeCard(name="Lava Spike", link="url", preview="prev")
        self.assertIn("Lava Spike", repr(card))
        self.assertIn("Lava Spike", str(card))


class TestArchetype(unittest.TestCase):
    def test_creation(self):
        arch = _make_archetype()
        self.assertEqual(arch.name, "Burn")
        self.assertEqual(arch.dominant_mana, ["R"])
        self.assertEqual(arch.staples, [])

    def test_creation_with_staples(self):
        staple = ArchetypeCard(name="Lightning Bolt", link="url", preview="prev")
        arch = _make_archetype(staples=[staple])
        self.assertEqual(len(arch.staples), 1)

    def test_hash_based_on_name(self):
        a1 = _make_archetype(name="Burn")
        a2 = _make_archetype(name="Burn", description="Different description.")
        self.assertEqual(hash(a1), hash(a2))

    def test_repr_and_str(self):
        arch = _make_archetype()
        self.assertIn("Burn", repr(arch))
        self.assertIn("Burn", str(arch))


class TestMetaShare(unittest.TestCase):
    def _ms(self, name, share):
        return MetaShare(
            mtggolfish_urls=[],
            meta_share=share,
            archetype_name=name,
            accuracy=0.9,
        )

    def test_creation(self):
        ms = self._ms("Burn", 0.25)
        self.assertEqual(ms.archetype_name, "Burn")
        self.assertAlmostEqual(ms.meta_share, 0.25)

    def test_lt(self):
        self.assertLess(self._ms("Burn", 0.1), self._ms("Faeries", 0.5))

    def test_not_lt_when_greater(self):
        self.assertFalse(self._ms("Faeries", 0.5) < self._ms("Burn", 0.1))

    def test_eq_by_archetype_name(self):
        ms1 = self._ms("Burn", 0.1)
        ms2 = self._ms("Burn", 0.9)
        self.assertEqual(ms1, ms2)

    def test_neq_different_archetype(self):
        self.assertNotEqual(self._ms("Burn", 0.5), self._ms("Faeries", 0.5))

    def test_eq_with_non_meta_share_returns_false(self):
        self.assertFalse(self._ms("Burn", 0.5) == "not a MetaShare")

    def test_lt_raises_on_wrong_type(self):
        with self.assertRaises(ValueError):
            _ = self._ms("Burn", 0.5) < "not a MetaShare"

    def test_repr_and_str(self):
        ms = self._ms("Burn", 0.25)
        self.assertIn("Burn", repr(ms))
        self.assertIn("Burn", str(ms))


class TestMetagame(unittest.TestCase):
    def test_creation(self):
        ms = MetaShare(
            mtggolfish_urls=[], meta_share=0.5, archetype_name="X", accuracy=1.0
        )
        mg = Metagame(meta_shares=[ms])
        self.assertEqual(len(mg.meta_shares), 1)

    def test_repr_and_str(self):
        mg = Metagame(meta_shares=[])
        self.assertIn("Metagame", str(mg))


class TestDPLDeck(unittest.TestCase):
    def test_creation(self):
        deck = DPLDeck(identifier="abc123", archetype="Burn", accuracy=0.95)
        self.assertEqual(deck.identifier, "abc123")
        self.assertEqual(deck.archetype, "Burn")
        self.assertAlmostEqual(deck.accuracy, 0.95)

    def test_hash_based_on_identifier(self):
        d1 = DPLDeck(identifier="abc", archetype="Burn", accuracy=0.9)
        d2 = DPLDeck(identifier="abc", archetype="Faeries", accuracy=0.5)
        self.assertEqual(hash(d1), hash(d2))

    def test_repr_and_str(self):
        deck = DPLDeck(identifier="x1", archetype="Burn", accuracy=1.0)
        self.assertIn("Burn", repr(deck))


class TestDPLMeta(unittest.TestCase):
    def test_identifier_property(self):
        meta = DPLMeta(name="DPL Season 1", dpl_decks=[])
        self.assertEqual(meta.identifier, "DPL Season 1")

    def test_hash_based_on_name(self):
        m1 = DPLMeta(name="Season 1", dpl_decks=[])
        m2 = DPLMeta(
            name="Season 1",
            dpl_decks=[DPLDeck(identifier="x", archetype="B", accuracy=1)],
        )
        self.assertEqual(hash(m1), hash(m2))

    def test_repr_and_str(self):
        meta = DPLMeta(name="Season 2", dpl_decks=[])
        self.assertIn("Season 2", str(meta))


class TestNewspauper(unittest.TestCase):
    def test_creation(self):
        news = Newspauper(news=[])
        self.assertEqual(news.news, [])

    def test_repr_and_str(self):
        news = Newspauper(news=[])
        self.assertIn("Newspauper", str(news))


class TestChangelog(unittest.TestCase):
    def test_creation(self):
        entry = ChangelogEntry(
            text="Added feature", date="2023-01-01", scope="all", link=None
        )
        cl = Changelog(changes=[entry])
        self.assertEqual(len(cl.changes), 1)

    def test_repr_and_str(self):
        cl = Changelog(changes=[])
        self.assertIn("Changelog", str(cl))


def _make_creator_sheet(**overrides):
    kwargs = dict(
        name="Alice",
        bio="A Pauper enthusiast.",
        mtgo_name="AliceMTGO",
        twitch_channel_url=None,
        youtube_channel_url=None,
        favorite_format=None,
        favorite_pauper_archetype=None,
        favorite_pauper_card_name=None,
        favorite_pauper_card_url=None,
        favorite_pauper_card_image_url=None,
        favorite_flavor_text_name=None,
        favorite_flavor_text_url=None,
        favorite_flavor_text_image_url=None,
        favorite_flavor_text_lines=None,
        favorite_artwork_name=None,
        favorite_artwork_url=None,
        favorite_artwork_image_url=None,
        favorite_artist_name=None,
        favorite_artist_gallery_url=None,
        favorite_magic_quote_lines=None,
    )
    kwargs.update(overrides)
    return CreatorSheet(**kwargs)


class TestCreatorSheet(unittest.TestCase):
    def test_creation(self):
        creator = _make_creator_sheet()
        self.assertEqual(creator.name, "Alice")
        self.assertEqual(creator.mtgo_name, "AliceMTGO")
        self.assertIsNone(creator.twitch_channel_url)

    def test_hash_based_on_name(self):
        p1 = _make_creator_sheet(name="Alice")
        p2 = _make_creator_sheet(name="Alice", bio="Different bio.")
        self.assertEqual(hash(p1), hash(p2))

    def test_repr_and_str(self):
        creator = _make_creator_sheet()
        self.assertIn("Alice", repr(creator))
        self.assertIn("Alice", str(creator))


class TestVideo(unittest.TestCase):
    def _make_video(self, **overrides):
        kwargs = dict(
            name="Burn vs Faeries",
            link="https://youtube.com/v/abc",
            language="en",
            creator_name="Alice",
            date="2023-06-15",
            archetype="Burn",
            video_id="abc123",
            deck_name="Burn 100.001.Alice",
        )
        kwargs.update(overrides)
        return Video(**kwargs)

    def test_creation(self):
        v = self._make_video()
        self.assertEqual(v.video_id, "abc123")
        self.assertEqual(v.archetype, "Burn")

    def test_hash_based_on_video_id(self):
        v1 = self._make_video(video_id="abc")
        v2 = self._make_video(video_id="abc", archetype="Faeries")
        self.assertEqual(hash(v1), hash(v2))

    def test_repr_and_str(self):
        v = self._make_video()
        self.assertIn("abc123", repr(v))


class TestDeck(unittest.TestCase):
    def _make_deck(self, **overrides):
        kwargs = dict(
            name="Burn 100.001.Alice",
            url="https://mtggoldfish.com/deck/1",
            archetype="Burn",
            set_name="Aether Revolt",
            set_date="2017-01-20",
            legal=True,
        )
        kwargs.update(overrides)
        return Deck(**kwargs)

    def test_creation(self):
        d = self._make_deck()
        self.assertEqual(d.name, "Burn 100.001.Alice")
        self.assertTrue(d.legal)

    def test_legal_false(self):
        d = self._make_deck(legal=False)
        self.assertFalse(d.legal)

    def test_hash_based_on_name(self):
        d1 = self._make_deck(name="Burn 100.001.Alice")
        d2 = self._make_deck(name="Burn 100.001.Alice", archetype="Faeries")
        self.assertEqual(hash(d1), hash(d2))

    def test_repr_and_str(self):
        d = self._make_deck()
        self.assertIn("Burn", repr(d))


class TestMTGGoldfishTournamentDeck(unittest.TestCase):
    def _make_deck(self, **overrides):
        kwargs = dict(
            url="https://mtggoldfish.com/deck/tournament/99",
            archetype="Faeries",
            place="1st",
            pilot="Bob",
            tabletop_price=None,
            mtgo_price=100,
            tournament_id="t1",
            tournament_name="Weekly Challenge",
            tournament_date="2023-06-01",
        )
        kwargs.update(overrides)
        return MTGGoldfishTournamentDeck(**kwargs)

    def test_creation(self):
        d = self._make_deck()
        self.assertEqual(d.archetype, "Faeries")
        self.assertEqual(d.place, "1st")

    def test_identifier_property(self):
        d = self._make_deck(url="https://mtggoldfish.com/deck/tournament/99")
        self.assertEqual(d.identifier, "99")

    def test_hash_based_on_identifier(self):
        d1 = self._make_deck(url="https://mtggoldfish.com/deck/tournament/42")
        d2 = self._make_deck(
            url="https://mtggoldfish.com/deck/tournament/42", archetype="Burn"
        )
        self.assertEqual(hash(d1), hash(d2))

    def test_repr_and_str(self):
        d = self._make_deck()
        self.assertIn("Faeries", repr(d))


class TestTournament(unittest.TestCase):
    def _make_tournament(self, **overrides):
        kwargs = dict(
            url="https://mtggoldfish.com/tournament/123",
            name="Pauper Challenge",
            date="2023-06-15",
            deck_ids=["d1", "d2"],
        )
        kwargs.update(overrides)
        return Tournament(**kwargs)

    def test_creation(self):
        t = self._make_tournament()
        self.assertEqual(t.name, "Pauper Challenge")
        self.assertEqual(t.deck_ids, ["d1", "d2"])

    def test_identifier_property(self):
        t = self._make_tournament(url="https://mtggoldfish.com/tournament/456")
        self.assertEqual(t.identifier, "456")

    def test_hash_based_on_identifier(self):
        t1 = self._make_tournament(url="https://mtggoldfish.com/tournament/7")
        t2 = self._make_tournament(
            url="https://mtggoldfish.com/tournament/7", name="Other"
        )
        self.assertEqual(hash(t1), hash(t2))

    def test_repr_and_str(self):
        t = self._make_tournament()
        self.assertIn("Pauper", repr(t))


class TestAcademyVideo(unittest.TestCase):
    def _make(self, **overrides):
        kwargs = dict(
            video_id="v999",
            user_name="streamer",
            title="Burn video",
            language="en",
            published_at="2023-06-15",
            deck_name="Burn 100.001",
            archetype="Burn",
            creator="Alice",
            url="https://twitch.tv/v999",
            fa_icon="fa-twitch",
        )
        kwargs.update(overrides)
        return AcademyVideo(**kwargs)

    def test_creation(self):
        v = self._make()
        self.assertEqual(v.video_id, "v999")
        self.assertEqual(v.archetype, "Burn")

    def test_hash_based_on_video_id(self):
        v1 = self._make(video_id="xyz")
        v2 = self._make(video_id="xyz", archetype="Faeries")
        self.assertEqual(hash(v1), hash(v2))

    def test_repr_and_str(self):
        v = self._make()
        self.assertIn("v999", repr(v))


if __name__ == "__main__":
    unittest.main()
