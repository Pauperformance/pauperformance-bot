import itertools
import math
from collections import defaultdict
from typing import DefaultDict, Optional, Tuple

from entity.deck.playable import PlayedCard

from pauperformance_bot.constant.mtg.game import BASIC_LANDS
from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.constant.pauperformance.silver import (
    BREW_CLASSIFICATION_THRESHOLD,
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
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


class Decklassifier:
    def __init__(
        self,
        pauperformance: PauperformanceService,
        academy_fs: AcademyFileSystem,
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.archetypes: list[ArchetypeConfig] = (
            self.pauperformance.config_reader.list_archetypes()
        )
        self.academy_fs: AcademyFileSystem = academy_fs
        self.known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = []
        self._decks_cache: dict[str, PlayableDeck] = {}
        self.load_training_data()

    def load_training_data(self):
        known_decks = self._load_mtggoldfish_tournament_training_data()
        other_known_decks = self._load_dpl_training_data()
        known_decks += other_known_decks
        # For better similarity results, we apply some assumptions on the decks.
        # Upon classification, we'll apply the same assumptions.
        for deck, _ in known_decks:
            self._simplify_deck(deck)
        self.known_decks = known_decks

    def _load_training_data(
        self, training_file, assets_data_deck_dir
    ) -> list[tuple[PlayableDeck, ArchetypeConfig]]:
        # Note: this method assumes all the decks in the training data are available in
        # the academy as .txt to load and parse.
        archetypes: list[ArchetypeConfig] = (
            self.pauperformance.config_reader.list_archetypes()
        )
        known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = []
        training_data = [
            tuple(line.split(","))
            for line in open(training_file, "r").read().splitlines()
            if line != "" and not line.startswith("#")
        ]
        for deck_id, archetype_name in training_data:
            playable_deck_path = posix_path(
                assets_data_deck_dir,
                f"{deck_id}.txt",
            )
            playable_deck: PlayableDeck = parse_playable_deck_from_lines(
                [line.strip() for line in open(playable_deck_path).readlines()]
            )
            try:
                archetype = next(a for a in archetypes if a.name == archetype_name)
                known_decks.append((playable_deck, archetype))
            except StopIteration:
                logger.error(
                    f"Unrecognized archetype label '{archetype_name}' for deck with "
                    f"id {deck_id}."
                )
                raise
        return known_decks

    def _load_mtggoldfish_tournament_training_data(
        self,
    ) -> list[tuple[PlayableDeck, ArchetypeConfig]]:
        config_reader = self.pauperformance.config_reader
        return self._load_training_data(
            config_reader.myr_file_system.MTGGOLDFISH_DECK_TRAINING_DATA,
            self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
        )

    def _load_dpl_training_data(
        self,
    ) -> list[tuple[PlayableDeck, ArchetypeConfig]]:
        return self._load_training_data(
            self.pauperformance.config_reader.myr_file_system.DPL_DECK_TRAINING_DATA,
            self.academy_fs.ASSETS_DATA_DECK_DPL_DIR,
        )

    def add_known_decks(self, known_decks: list[tuple[PlayableDeck, ArchetypeConfig]]):
        self.known_decks += known_decks

    @staticmethod
    def _magnitude(cards_map: dict) -> float:
        return math.sqrt(sum(qty * qty for qty in cards_map.values()))

    @staticmethod
    def _sparse_cosine_similarity(
        cards_map1: dict, mag1: float, cards_map2: dict, mag2: float, w: float = 1.0
    ) -> float:
        if w == 0:
            return 1.0
        if mag1 == 0 or mag2 == 0:
            return 0.0
        dot = sum(
            cards_map1[c] * cards_map2[c]
            for c in cards_map1.keys() & cards_map2.keys()
        )
        return dot / (mag1 * mag2)

    def get_similarity(self, deck1: PlayableDeck, deck2: PlayableDeck) -> float:
        logger.debug("Computing similarity between decks...")
        main1, main2 = deck1.mainboard_cards_map, deck2.mainboard_cards_map
        side1, side2 = deck1.sideboard_cards_map, deck2.sideboard_cards_map
        sim_main = self._sparse_cosine_similarity(
            main1, self._magnitude(main1), main2, self._magnitude(main2), MAINBOARD_WEIGHT
        )
        logger.debug(f"Mainboard similarity: {sim_main}")
        sim_side = self._sparse_cosine_similarity(
            side1, self._magnitude(side1), side2, self._magnitude(side2), SIDEBOARD_WEIGHT
        )
        logger.debug(f"sideboard similarity: {sim_side}")
        # give same weight to main and sideboard:
        # sim = (sim_main + sim_side) / 2
        # alternatively, give different weights:
        w_sim_main = 3
        w_sim_side = 1
        sim = (w_sim_main * sim_main + w_sim_side * sim_side) / (w_sim_main + w_sim_side)
        logger.debug(f"Computed similarity between decks: {sim}.")
        return sim

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
    ) -> Tuple[ArchetypeConfig, Optional[float]]:
        logger.debug("Classifying deck...")
        most_similar_archetype, highest_similarity = None, 0

        # for better similarity results, we are going to make some assumptions on decks
        self._simplify_deck(deck)

        # TODO: remove this block in the future if it becomes useless
        # first, check if archetype can be detected with rules
        archetype_predicates = [
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

        # second, compare with other known decks
        for archetype in self.archetypes:
            if not deck.can_belong_to_archetype(archetype):
                logger.debug(f"Skipping archetype {archetype.name} due to rules...")
                continue
            logger.debug(f"Comparing deck with reference lists of {archetype.name}...")
            for reference_deck in archetype.reference_decks:
                logger.debug(f"Comparing deck with reference list {reference_deck}...")
                if reference_deck not in self._decks_cache:
                    playable_reference_deck = self.pauperformance.get_playable_deck(
                        reference_deck
                    )
                    # for better similarity results, apply same assumptions as above
                    self._simplify_deck(playable_reference_deck)
                    self._decks_cache[reference_deck] = playable_reference_deck
                deck2 = self._decks_cache[reference_deck]
                logger.debug(f"Compared deck with reference list {reference_deck}.")
                score = self.get_similarity(deck, deck2)
                logger.debug(f"Similarity: {score}.")
                if score > highest_similarity:
                    most_similar_archetype, highest_similarity = archetype, score
                logger.debug(f"Compared deck with reference lists of {archetype.name}.")

        logger.debug("Comparing deck with known decks...")
        for deck2, archetype in self.known_decks:
            # known_decks were simplified upon loading
            if not deck.can_belong_to_archetype(archetype):
                continue
            score = self.get_similarity(deck, deck2)
            logger.debug(f"Similarity: {score}.")
            if score > highest_similarity:
                most_similar_archetype, highest_similarity = archetype, score
        logger.debug("Compared deck with known decks.")
        logger.debug("Classified deck.")
        return most_similar_archetype, highest_similarity

    def _simplify_deck(self, playable_deck: PlayableDeck):
        # In Pauper, only few decks take advantage of Snow-Covered lands.
        # However, Snow-Covered lands are often used for no reason.
        swap_tuples = [(f"Snow-Covered {land}", land) for land in BASIC_LANDS]

        # Hydroblast and Blue Elemental Blast should be considered equivalent.
        # Same holds for Pyroblast and Red Elemental Blast.
        swap_tuples += [
            ("Blue Elemental Blast", "Hydroblast"),
            ("Red Elemental Blast", "Pyroblast"),
        ]

        # TODO: treat equals UB and IU versions of the same card

        self._simplify_mainboard(playable_deck, swap_tuples)
        self._simplify_sideboard(playable_deck, swap_tuples)

    @staticmethod
    def _simplify_mainboard(playable_deck: PlayableDeck, swap_tuples):
        for old_card, new_card in swap_tuples:
            if old_card in playable_deck.mainboard_cards_map:
                old_amount = playable_deck.mainboard_cards_map[old_card]
                playable_deck.remove_mainboard_card(PlayedCard(old_amount, old_card))
                playable_deck.add_mainboard_card(PlayedCard(old_amount, new_card))

    @staticmethod
    def _simplify_sideboard(playable_deck: PlayableDeck, swap_tuples):
        for old_card, new_card in swap_tuples:
            if old_card in playable_deck.sideboard_cards_map:
                old_amount = playable_deck.sideboard_cards_map[old_card]
                playable_deck.remove_sideboard_card(PlayedCard(old_amount, old_card))
                playable_deck.add_sideboard_card(PlayedCard(old_amount, new_card))

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
        lines += [""]
        playable_deck = parse_playable_deck_from_lines(
            lines, raise_error_if_invalid=False
        )
        return deck_id, playable_deck

    def get_dpl_metagame(
        self,
        decks,
        name="DPL metagame",
        brew_threshold=BREW_CLASSIFICATION_THRESHOLD,
        learn_on_the_fly=True,
    ):
        dpl_decks = []
        for deck in decks:
            deck_id, playable_deck = self.parse_dpl_deck(deck)
            most_similar_archetype, highest_similarity = self.classify_deck(
                playable_deck
            )
            if highest_similarity < brew_threshold:
                most_similar_archetype = None
            elif learn_on_the_fly:
                self.known_decks.append((playable_deck, most_similar_archetype))
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
