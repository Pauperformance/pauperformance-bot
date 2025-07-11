import itertools
from collections import defaultdict
from typing import DefaultDict, Tuple

from scipy import spatial

from pauperformance_bot.constant.pauperformance.silver import (
    MAINBOARD_WEIGHT,
    SIDEBOARD_WEIGHT,
)
from pauperformance_bot.entity.api.miscellanea import (
    DPLDeck,
    DPLMeta,
    Metagame,
    MetaShare,
)
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.mtg.mtggoldfish import MTGGoldfish
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.math import truncate

logger = get_application_logger()


class Decklassifier:
    def __init__(
        self,
        pauperformance: PauperformanceService,
        known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = None,
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.archetypes: list[ArchetypeConfig] = (
            self.pauperformance.config_reader.list_archetypes()
        )
        self.known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = (
            known_decks if known_decks else []
        )
        self._decks_cache: dict[str, PlayableDeck] = {}

    def add_known_decks(self, known_decks: list[tuple[PlayableDeck, ArchetypeConfig]]):
        self.known_decks += known_decks

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
        # sim = (sim_main + sim_side) / 2
        # alternatively, give different weights
        w_sim_main = 3
        w_sim_side = 1
        sim = (w_sim_main * sim_main + w_sim_side * sim_side) / (
            w_sim_main + w_sim_side
        )
        logger.debug(f"Computed similarity between decks: {sim}.")
        return sim

    def _is_affinity(self, deck: PlayableDeck) -> bool:
        artifact_lands = self.pauperformance.scryfall.get_legal_artifact_lands()
        artifact_lands_names = [c["name"] for c in artifact_lands]
        affinity_creatures = [
            "Frogmite",
            "Atog",
            "Myr Enforcer",
            "Carapace Forger",
            "Sojourner's Companion",
            "Somber Hoverguard",
        ]
        has_artifact_mana_base = (
            len([c for c in artifact_lands_names if c in deck]) >= 4
        )
        has_affinity_creatures = len([c for c in affinity_creatures if c in deck]) >= 2
        if (
            has_artifact_mana_base
            and has_affinity_creatures
            and "Galvanic Blast" in deck
        ):
            return True
        return False

    def _is_flicker_tron(self, deck: PlayableDeck) -> bool:
        return all(
            c in deck
            for c in (
                "Urza's Mine",
                "Urza's Tower",
                "Urza's Power Plant",
                "Ghostly Flicker",
            )
        )

    def _is_empty_the_warrens_storm(self, deck: PlayableDeck) -> bool:
        return all(
            c in deck for c in ("Empty the Warrens", "Dark Ritual", "Cabal Ritual")
        )

    def _is_goblins(self, deck: PlayableDeck) -> bool:
        return all(
            c in deck
            for c in ("Sparksmith", "Mountain", "Goblin Bushwhacker", "Mogg Conscripts")
        )

    def _is_monow_heroic(self, deck: PlayableDeck) -> bool:
        return all(
            c in deck
            for c in ("Lagonna-Band Trailblazer", "Hyena Umbra", "Deftblade Elite")
        )

    def _is_izzet_blitz(self, deck: PlayableDeck) -> bool:
        blitz_creatures = [
            "Kiln Fiend",
            "Nivix Cyclops",
            "Wee Dragonauts",
        ]
        return len([c for c in blitz_creatures if c in deck]) >= 2

    def _is_monob_control(self, deck: PlayableDeck) -> bool:
        monob_control_cards = [
            "Gray Merchant of Asphodel",
            "Cuombajj Witches",
            "Oubliette",
            "Chittering Rats",
            "Tendrils of Corruption",
            "Chainer's Edict",
            "Sign in Blood",
        ]
        return len([c for c in monob_control_cards if c in deck]) >= 3

    def _is_infect(self, deck: PlayableDeck) -> bool:
        infect_creatures = [
            "Glistener Elf",
            "Llanowar Augur",
            "Blight Mamba",
            "Ichorclaw Myr",
            "Rot Wolf",
        ]
        return len([c for c in infect_creatures if c in deck]) >= 3

    def _is_walls(self, deck: PlayableDeck) -> bool:
        walls_creatures = [
            "Overgrown Battlement",
            "Axebane Guardian",
            "Valakut Invoker",
            "Secret Door",
            "Galvanic Alchemist",
            "Shield-Wall Sentinel",
        ]
        return len([c for c in walls_creatures if c in deck]) >= 3

    def _is_azorius_prowess(self, deck: PlayableDeck) -> bool:
        azorius_creatures = [
            "Seeker of the Way",
            "Elusive Spellfist",
            "Jhessian Thief",
            "Delver of Secrets",
        ]
        return len([c for c in azorius_creatures if c in deck]) >= 3

    def classify_deck(
        self,
        deck: PlayableDeck,
    ) -> Tuple[ArchetypeConfig, float]:
        logger.debug("Classifying deck...")
        most_similar_archetype, highest_similarity = None, 0

        # TODO: remove this block in the future if it becomes useless
        # First, check if archetype can be detected with rules.
        archetype_predicates = [
            ("Affinity", self._is_affinity),
            ("Flicker Tron", self._is_flicker_tron),
            ("Empty The Warrens Storm", self._is_empty_the_warrens_storm),
            ("Goblins", self._is_goblins),
            ("MonoW Heroic", self._is_monow_heroic),
            ("Izzet Blitz", self._is_izzet_blitz),
            ("MonoB Control", self._is_monob_control),
            ("Infect", self._is_infect),
            ("Walls", self._is_walls),
            ("Azorius Prowess", self._is_azorius_prowess),
        ]
        for archetype_name, archetype_predicate in archetype_predicates:
            if archetype_predicate(deck) and deck.can_belong_to_archetype(
                next(a for a in self.archetypes if a.name == archetype_name)
            ):
                logger.debug(f"Deck is {archetype_name}.")
                return next(a for a in self.archetypes if a.name == archetype_name), 1.0

        # Second, compare with other known decks.
        for archetype in self.archetypes:
            if not deck.can_belong_to_archetype(archetype):
                logger.debug(f"Skipping archetype {archetype.name} due to rules...")
                continue
            logger.debug(f"Comparing deck with reference lists of {archetype.name}...")
            for reference_deck in archetype.reference_decks:
                logger.debug(f"Comparing deck with reference list {reference_deck}...")
                if reference_deck not in self._decks_cache:
                    self._decks_cache[reference_deck] = (
                        self.pauperformance.get_playable_deck(reference_deck)
                    )
                deck2 = self._decks_cache[reference_deck]
                logger.debug(f"Compared deck with reference list {reference_deck}.")
                score = self.get_similarity(deck, deck2)
                logger.debug(f"Similarity: {score}.")
                if score > highest_similarity:
                    most_similar_archetype, highest_similarity = archetype, score
                logger.debug(f"Compared deck with reference lists of {archetype.name}.")

        logger.debug("Comparing deck with known decks...")
        for deck2, archetype in self.known_decks:
            score = self.get_similarity(deck, deck2)
            logger.debug(f"Similarity: {score}.")
            if score > highest_similarity and deck.can_belong_to_archetype(archetype):
                most_similar_archetype, highest_similarity = archetype, score
        logger.debug("Compared deck with known decks.")
        logger.debug("Classified deck.")
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

    def parse_dpl_deck(self, deck):
        deck_id = deck["id"]
        lines = [f"{pc['quantity']} {pc['name']}" for pc in deck["cards"]["mainboard"]]
        lines += [""]
        lines += [f"{pc['quantity']} {pc['name']}" for pc in deck["cards"]["sideboard"]]
        playable_deck = parse_playable_deck_from_lines(
            lines, raise_error_if_invalid=False
        )
        return deck_id, playable_deck

    def get_dpl_metagame(self, decks, name="DPL metagame"):
        dpl_decks = []
        for deck in decks:
            deck_id, playable_deck = self.parse_dpl_deck(deck)
            most_similar_archetype, highest_similarity = self.classify_deck(
                playable_deck
            )
            logger.info(f"{deck} | {most_similar_archetype} {highest_similarity}")
            if highest_similarity < 0.76:
                most_similar_archetype = None
            dpl_decks.append(
                DPLDeck(
                    identifier=deck_id,
                    archetype=(
                        most_similar_archetype.name
                        if most_similar_archetype
                        else "Brew"
                    ),
                    accuracy=float(highest_similarity),
                )
            )
        dpl_meta = DPLMeta(
            name=name,
            dpl_decks=dpl_decks,
        )
        logger.info(dpl_meta)
        archetype_maps = defaultdict(int)
        for dpl_deck in dpl_meta.dpl_decks:
            if not dpl_deck.archetype:
                print(f"WARNING: manually count {dpl_deck}")
                continue
            archetype_maps[dpl_deck.archetype] += 1
        game_types = defaultdict(int)
        print()
        for k, v in sorted(archetype_maps.items()):
            print(f"{v} {k}")
            for a in self.archetypes:
                if a.name == k:
                    # some decks have multiple game styles: let's use the first one
                    game_types[a.game_type[0]] += 1
                    break
        print()
        for k, v in sorted(game_types.items()):
            print(f"{v} {k}")
        return dpl_meta
