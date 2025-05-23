import os
from pathlib import Path

import jsonpickle

from pauperformance_bot.constant.mtg.mtggoldfish import DECK_API_ENDPOINT
from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.api.tournament import Tournament
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
        academy_fs: AcademyFileSystem = AcademyFileSystem(),
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.archetypes: list[ArchetypeConfig] = (
            self.pauperformance.config_reader.list_archetypes()
        )
        self.academy_fs: AcademyFileSystem = academy_fs

    def check_all(self):
        return all(
            (
                self.check_archetypes_rules_for_archived_decks(),
                self.check_archetypes_rules_for_classified_decks(),
                self.check_mtg_tournament_decks_are_downloaded(),
            )
        )

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

    def check_archetypes_rules_for_classified_decks(self) -> bool:
        logger.info("Checking must/must-not-have rules for classified decks...")
        # if a deck has been classified it means it has first been downloaded
        rm_cmds = []
        for deck_path in Path(self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob(
            "*.json"
        ):
            deck: Deck = jsonpickle.decode(open(deck_path).read())
            if deck.url.startswith(DECK_API_ENDPOINT):
                mtggoldfish_deck_id = deck.url.rsplit("/")[-1]
                playable_deck_path = posix_path(
                    self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                    f"{mtggoldfish_deck_id}.txt",
                )
            else:
                logger.warning(f"Unable to check archetype rules for deck {deck_path}.")
                continue
            try:
                playable_deck: PlayableDeck = parse_playable_deck_from_lines(
                    [line.strip() for line in open(playable_deck_path).readlines()]
                )
            except ValueError:
                rm_cmds.append(f'rm "{deck_path}"')
                continue
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
                rm_cmds.append(f'rm "{deck_path}"')
                return False
        # print("\n".join(rm_cmds))
        return True

    def check_mtg_tournament_decks_are_downloaded(self):
        fs = self.academy_fs
        goldfish_tournaments_dir = fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DIR
        json_goldfish_decks_dir = fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DECKS_DIR
        raw_goldfish_decks_dir = fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR
        for tournament_file in Path(goldfish_tournaments_dir).glob("*.json"):
            tournament: Tournament = jsonpickle.decode(open(tournament_file).read())
            for deck_id in tournament.deck_ids:
                if not os.path.exists(
                    json_goldfish_decks_dir + os.path.sep + deck_id + ".json"
                ):
                    logger.warning(
                        f"Missing {deck_id}.json from tournament {tournament_file}."
                    )
                    return False
                if not os.path.exists(
                    raw_goldfish_decks_dir + os.path.sep + deck_id + ".txt"
                ):
                    logger.warning(
                        f"Missing {deck_id}.txt from tournament {tournament_file}."
                    )
                    return False
        return True
