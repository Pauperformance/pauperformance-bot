import itertools
from collections import defaultdict
from typing import DefaultDict, Tuple

from scipy import spatial

from pauperformance_bot.constant.pauperformance.silver import (
    MAINBOARD_WEIGHT,
    SIDEBOARD_WEIGHT,
)
from pauperformance_bot.entity.api.miscellanea import Metagame, MetaShare
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.mtg.mtggoldfish import MTGGoldfish
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.math import truncate

logger = get_application_logger()


class SilverService:
    def __init__(self, pauperformance: PauperformanceService):
        self.pauperformance: PauperformanceService = pauperformance

    @staticmethod
    def _cosine_similarity(v1, v2, w=1.0):
        if w == 0:
            return 1
        return 1 - spatial.distance.cosine(v1, v2, w=len(v1) * [w])

    @staticmethod
    def _vectorize(cards_map1, cards_map2):
        # In Pauper, only few decks take advantage of Snow-Covered lands.
        # However, Snow-Covered lands are often used.
        # For better similarity results, we want Snow-Covered lands to be treated as
        # normal lands.
        basic_lands = ["Forest", "Island", "Mountain", "Plains", "Swamp"]
        for card_map in (cards_map1, cards_map2):
            for land in basic_lands:
                snow_land = f"Snow-Covered {land}"
                if snow_land in card_map:
                    snow_amount = card_map[snow_land]
                    non_snow_amount = card_map.get(land, 0)
                    del card_map[snow_land]
                    card_map[land] = snow_amount + non_snow_amount

        # Hydroblast and Blue Elemental Blast should be considered equivalent.
        # Same holds for Pyroblast and Red Elemental Blast.
        for card_map in (cards_map1, cards_map2):
            if "Blue Elemental Blast" in card_map:
                beb_amount = card_map["Blue Elemental Blast"]
                hydro_amount = card_map.get("Hydroblast", 0)
                del card_map["Blue Elemental Blast"]
                card_map["Hydroblast"] = beb_amount + hydro_amount
            if "Red Elemental Blast" in card_map:
                beb_amount = card_map["Red Elemental Blast"]
                hydro_amount = card_map.get("Pyroblast", 0)
                del card_map["Red Elemental Blast"]
                card_map["Pyroblast"] = beb_amount + hydro_amount

        all_cards = list(set(cards_map1.keys()).union(set(cards_map2.keys())))
        all_cards.sort()
        return (
            [cards_map1.get(c, 0) for c in all_cards],
            [cards_map2.get(c, 0) for c in all_cards],
        )

    def get_similarity(self, deck1: PlayableDeck, deck2: PlayableDeck) -> float:
        logger.debug("Computing similarity between decks...")
        vector_main1, vector_main2 = self._vectorize(
            deck1.mainboard_cards_map,
            deck2.mainboard_cards_map,
        )
        vector_side1, vector_side2 = self._vectorize(
            deck1.sideboard_cards_map,
            deck2.sideboard_cards_map,
        )
        sim_main = self._cosine_similarity(vector_main1, vector_main2, MAINBOARD_WEIGHT)
        logger.debug(f"Mainboard similarity: {sim_main}")
        sim_side = self._cosine_similarity(vector_side1, vector_side2, SIDEBOARD_WEIGHT)
        logger.debug(f"sideboard similarity: {sim_side}")
        sim = (sim_main + sim_side) / 2
        logger.debug(f"Computed similarity between decks: {sim}.")
        return sim

    def classify_deck(
        self,
        deck: PlayableDeck,
    ) -> Tuple[ArchetypeConfig, float]:
        logger.debug("Classifying deck...")
        archetypes = self.pauperformance.config_reader.list_archetypes()
        most_similar_archetype = None
        highest_similarity = 0
        for archetype in archetypes:
            logger.debug(f"Comparing deck with reference lists of {archetype.name}...")
            for reference_deck in archetype.reference_decks:
                logger.debug(f"Comparing deck with reference list {reference_deck}...")
                deck2 = self.pauperformance.get_playable_deck(reference_deck)
                logger.debug(f"Compared deck with reference list {reference_deck}.")
                score = self.get_similarity(deck, deck2)
                logger.debug(f"Similarity: {score}.")
                if score > highest_similarity:
                    logger.debug("Updated most similar deck.")
                    highest_similarity = score
                    most_similar_archetype = archetype
                logger.debug(f"Compared deck with reference lists of {archetype.name}.")
        logger.debug("Classifying deck...")
        return most_similar_archetype, highest_similarity

    def get_metagame(self) -> Metagame:
        mtggoldfish = MTGGoldfish()
        mtggoldfish_meta = mtggoldfish.get_pauper_meta()
        meta_shares: DefaultDict[str, list[MetaShare]] = defaultdict(list)
        for link, values in mtggoldfish_meta.items():
            share, playable_deck = values
            similar_archetype, similarity_score = self.classify_deck(playable_deck)
            archetype_name = similar_archetype.name
            if similarity_score < 0.30:
                archetype_name = "Brew"
                similarity_score = 1 - similarity_score
            meta_share = MetaShare(
                mtggolfish_urls=[link],
                meta_share=float(share[:-1]),  # drop trailing '%'
                archetype_name=archetype_name,
                accuracy=truncate(similarity_score * 100, 1),  # similarity is in [0, 1]
            )
            meta_shares[archetype_name].append(meta_share)
        # if possible, merge meta_shares
        grouped_meta_shares: list[MetaShare] = []
        for archetype, shares in meta_shares.items():
            if len(shares) == 1:
                grouped_meta_shares.append(shares[0])
                continue
            logger.debug(
                f"Merging {len(shares)} shares for the same archetype ({archetype})..."
            )
            grouped_meta_shares.append(
                MetaShare(
                    mtggolfish_urls=list(
                        itertools.chain(*(s.mtggolfish_urls for s in shares))
                    ),
                    meta_share=sum(s.meta_share for s in shares),
                    archetype_name=archetype,
                    accuracy=sum(s.accuracy for s in shares) / len(shares),
                )
            )
        return Metagame(meta_shares=grouped_meta_shares)
