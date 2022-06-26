from pathlib import Path

import jsonpickle

from pauperformance_bot.constant.mtg.mtggoldfish import DECK_API_ENDPOINT
from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


class Checker:
    def __init__(
        self,
        pauperformance: PauperformanceService,
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.archetypes: list[
            ArchetypeConfig
        ] = self.pauperformance.config_reader.list_archetypes()

    def check_archetypes_rules_for_archived_decks(self) -> bool:
        logger.info("Checking must/must-not-have rules for archived decks...")
        for archived_deck in self.pauperformance.list_archived_decks():
            playable_deck = self.pauperformance.get_playable_deck(
                archived_deck.p12e_name
            )
            archetype = next(
                a
                for a in self.archetypes
                if a.name == archived_deck.archetype
                or archived_deck.archetype in a.aliases
            )
            if not playable_deck.can_belong_to_archetype(archetype):
                logger.warning(
                    f"Deck {archived_deck.p12e_name} violates {archetype.name} rules."
                )
                return False
        return True

    def check_archetypes_rules_for_classified_decks(
        self, academy_fs: AcademyFileSystem = AcademyFileSystem()
    ) -> bool:
        logger.info("Checking must/must-not-have rules for classified decks...")
        # if a deck has been classified it means it has first been downloaded
        for deck_path in Path(academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob("*.json"):
            deck: Deck = jsonpickle.decode(open(deck_path).read())
            if deck.url.startswith(DECK_API_ENDPOINT):
                mtggoldfish_deck_id = deck.url.rsplit("/")[-1]
                playable_deck_path = posix_path(
                    academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                    f"{mtggoldfish_deck_id}.txt",
                )
            else:
                logger.warning(f"Unable to check archetype rules for deck {deck_path}.")
                continue
            playable_deck: PlayableDeck = parse_playable_deck_from_lines(
                [line.strip() for line in open(playable_deck_path).readlines()]
            )
            archetype = next(
                a
                for a in self.archetypes
                if a.name == deck.archetype or deck.archetype in a.aliases
            )
            if not playable_deck.can_belong_to_archetype(archetype):
                logger.warning(
                    f"Deck {deck.url} ({deck_path}) violates "
                    f"{archetype.name} rules."
                )
                return False
        return True
