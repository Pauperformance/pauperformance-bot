from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
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
    deck = _make_deck({
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
    })

    classifier = Decklassifier.from_snapshot_data(
        archetypes=archetypes,
        known_decks=[],
        decks_cache={},
        artifact_land_names=artifact_land_names,
    )

    assert classifier._is_affinity(deck) is True
