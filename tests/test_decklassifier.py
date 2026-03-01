import os
import pickle
import tempfile

from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier


def _make_archetype(name, must_have=None, must_not_have=None, reference_decks=None):
    return ArchetypeConfig(
        name=name,
        aliases=[],
        family=None,
        dominant_mana=[],
        game_type=["Aggro"],
        description="",
        must_have_cards=must_have or [],
        must_not_have_cards=must_not_have or [],
        reference_decks=reference_decks or [],
        resource_sideboard=None,
        resources_discord=[],
        resources=[],
    )


def _make_deck(mainboard_cards, sideboard_cards=None):
    mainboard = [PlayedCard(qty, name) for name, qty in mainboard_cards.items()]
    sideboard = [PlayedCard(qty, name) for name, qty in (sideboard_cards or {}).items()]
    return PlayableDeck(mainboard, sideboard, raise_error_if_invalid=False)


def test_is_affinity_with_preloaded_artifact_lands():
    """_is_affinity should use pre-loaded artifact land names when available."""
    archetype = _make_archetype("Affinity")
    archetypes = [archetype]

    artifact_land_names = [
        "Ancient Den",
        "Great Furnace",
        "Seat of the Synod",
        "Tree of Tales",
        "Vault of Whispers",
        "Darksteel Citadel",
        "Mistvault Bridge",
        "Razortide Bridge",
        "Rustvale Bridge",
        "Silverbluff Bridge",
        "Slagwoods Bridge",
        "Tanglepool Bridge",
        "Thornglint Bridge",
        "Drossforge Bridge",
        "Goldmire Bridge",
    ]

    # Build an Affinity deck
    deck = _make_deck(
        {
            "Ancient Den": 4,
            "Great Furnace": 4,
            "Seat of the Synod": 4,
            "Tree of Tales": 4,
            "Frogmite": 4,
            "Myr Enforcer": 4,
            "Galvanic Blast": 4,
            "Thoughtcast": 4,
            "Chromatic Star": 4,
            "Springleaf Drum": 4,
            "Island": 4,
            "Ornithopter": 4,
            "Somber Hoverguard": 4,
            "Atog": 4,
            "Disciple of the Vault": 4,
        }
    )

    classifier = Decklassifier.from_snapshot_data(
        archetypes=archetypes,
        known_decks=[],
        decks_cache={},
        artifact_land_names=artifact_land_names,
    )

    assert classifier._is_affinity(deck) is True


def test_is_not_affinity_with_preloaded_artifact_lands():
    """_is_affinity should return False for a non-Affinity deck."""
    artifact_land_names = ["Ancient Den", "Great Furnace", "Seat of the Synod"]

    # A Burn deck - no artifact lands, no affinity creatures
    deck = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 2,
            "Searing Blaze": 4,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[],
        known_decks=[],
        decks_cache={},
        artifact_land_names=artifact_land_names,
    )

    assert classifier._is_affinity(deck) is False


def test_classify_deck_with_known_decks():
    """Classifier should find the most similar archetype from known_decks."""
    burn_archetype = _make_archetype("Burn")
    elves_archetype = _make_archetype("Elves")

    known_burn = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 2,
            "Searing Blaze": 4,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    new_burn = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 4,
            "Searing Blaze": 2,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[burn_archetype, elves_archetype],
        known_decks=[(known_burn, burn_archetype)],
        decks_cache={},
        artifact_land_names=[],
    )

    archetype, similarity = classifier.classify_deck(new_burn)
    assert archetype.name == "Burn"
    assert similarity > 0.9


def test_classify_deck_with_precached_reference_decks():
    """Classifier should use _decks_cache for reference decks without calling pauperformance."""
    burn_archetype = _make_archetype("Burn", reference_decks=["burn_ref_1"])

    burn_ref_deck = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 2,
            "Searing Blaze": 4,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    new_burn = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 4,
            "Searing Blaze": 2,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[burn_archetype],
        known_decks=[],
        decks_cache={"burn_ref_1": burn_ref_deck},
        artifact_land_names=[],
    )

    archetype, similarity = classifier.classify_deck(new_burn)
    assert archetype.name == "Burn"
    assert similarity > 0.9


def test_classify_deck_skips_uncached_reference_when_no_pauperformance():
    """When pauperformance is None and reference deck is not cached, skip it gracefully."""
    burn_archetype = _make_archetype("Burn", reference_decks=["missing_ref_1"])

    known_burn = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 2,
            "Searing Blaze": 4,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    new_burn = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 4,
            "Searing Blaze": 2,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[burn_archetype],
        known_decks=[(known_burn, burn_archetype)],
        decks_cache={},
        artifact_land_names=[],
    )

    archetype, similarity = classifier.classify_deck(new_burn)
    assert archetype.name == "Burn"
    assert similarity > 0.9


def test_from_snapshot_loads_from_file():
    """Decklassifier.from_snapshot should load classifier state from a pickle file."""
    burn_archetype = _make_archetype("Burn")
    known_burn = _make_deck(
        {
            "Lightning Bolt": 4,
            "Lava Spike": 4,
            "Rift Bolt": 4,
            "Chain Lightning": 4,
            "Fireblast": 2,
            "Searing Blaze": 4,
            "Ghitu Lavarunner": 4,
            "Thermo-Alchemist": 4,
            "Mountain": 18,
            "Needle Drop": 4,
            "Skewer the Critics": 4,
            "Shard Volley": 4,
        }
    )

    snapshot = {
        "archetypes": [burn_archetype],
        "known_decks": [(known_burn, burn_archetype)],
        "decks_cache": {},
        "artifact_land_names": ["Ancient Den", "Great Furnace"],
    }

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        pickle.dump(snapshot, f)
        snapshot_path = f.name

    try:
        classifier = Decklassifier.from_snapshot(snapshot_path)
        assert len(classifier.archetypes) == 1
        assert classifier.archetypes[0].name == "Burn"
        assert len(classifier.known_decks) == 1
        assert classifier._artifact_land_names == ["Ancient Den", "Great Furnace"]
        assert classifier.pauperformance is None
    finally:
        os.unlink(snapshot_path)
