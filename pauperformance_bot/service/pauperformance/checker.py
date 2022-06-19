import time
from pathlib import Path

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.util.log import get_application_logger

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
        for deck in self.pauperformance.list_archived_decks():
            playable_deck = self.pauperformance.get_playable_deck(deck.p12e_name)
            archetype = next(
                a
                for a in self.archetypes
                if a.name == deck.archetype or deck.archetype in a.aliases
            )
            if not playable_deck.can_belong_to_archetype(archetype):
                logger.warning(
                    f"Deck {deck.p12e_name} violates {archetype.name} rules."
                )
                return False
        return True

    def check_archetypes_rules_for_classified_decks(
        self, academy_fs: AcademyFileSystem = AcademyFileSystem()
    ) -> bool:
        logger.info("Checking must/must-not-have rules for classified decks...")
        for deck_file in Path(academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob("*.json"):
            time.sleep(2)
            deck: Deck = jsonpickle.decode(open(deck_file).read())
            download_url = deck.url.replace("/deck", "/deck/download")
            deck_downloader = MtgoDeckDownloader(download_url)
            playable_deck = deck_downloader.download()
            archetype = next(
                a
                for a in self.archetypes
                if a.name == deck.archetype or deck.archetype in a.aliases
            )
            if not playable_deck.can_belong_to_archetype(archetype):
                logger.warning(
                    f"Deck {deck.p12e_name} violates {archetype.name} rules."
                )
                # os.remove(deck_file)  # TODO: enable if necessary
                return False
        return True
