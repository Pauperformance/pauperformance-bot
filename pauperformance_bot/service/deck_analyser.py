from typing import Tuple

from scipy import spatial

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()

MAINBOARD_WEIGHT = 1
SIDEBOARD_WEIGHT = 0.25


def _cosine_similarity(v1, v2, w=1.0):
    if w == 0:
        return 1
    return 1 - spatial.distance.cosine(v1, v2, w=len(v1) * [w])


def _vectorize(cards_map1, cards_map2):
    all_cards = list(set(cards_map1.keys()).union(set(cards_map2.keys())))
    all_cards.sort()
    return (
        [cards_map1.get(c, 0) for c in all_cards],
        [cards_map2.get(c, 0) for c in all_cards],
    )


def get_similarity(deck1: PlayableDeck, deck2: PlayableDeck) -> float:
    logger.debug("Computing similarity between decks...")
    vector_main1, vector_main2 = _vectorize(
        deck1.mainboard_cards_map,
        deck2.mainboard_cards_map,
    )
    vector_side1, vector_side2 = _vectorize(
        deck1.sideboard_cards_map,
        deck2.sideboard_cards_map,
    )
    sim_main = _cosine_similarity(vector_main1, vector_main2, MAINBOARD_WEIGHT)
    logger.debug(f"Mainboard similarity: {sim_main}")
    sim_side = _cosine_similarity(vector_side1, vector_side2, SIDEBOARD_WEIGHT)
    logger.debug(f"sideboard similarity: {sim_side}")
    sim = sim_main * sim_side
    logger.debug(f"Computed similarity between decks: {sim}.")
    return sim


def classify_deck(
    deck: PlayableDeck, pauperformance: PauperformanceService
) -> Tuple[str, float]:
    logger.debug("Classifying deck...")
    archetypes = pauperformance.config_reader.list_archetypes()
    most_similar_deck = ""
    highest_similarity = 0
    for archetype in archetypes:
        logger.debug(f"Comparing deck with reference lists of {archetype.name}...")
        for reference_deck in archetype.reference_decks:
            logger.debug(f"Comparing deck with reference list {reference_deck}...")
            deck2 = pauperformance.get_playable_deck(reference_deck)
            logger.debug(f"Compared deck with reference list {reference_deck}.")
            score = get_similarity(deck, deck2)
            logger.debug(f"Similarity: {score}.")
            if score > highest_similarity:
                logger.debug("Updated most similar deck.")
                highest_similarity = score
                most_similar_deck = reference_deck
            logger.debug(f"Compared deck with reference lists of {archetype.name}.")
    logger.debug("Classifying deck...")
    return most_similar_deck, highest_similarity
