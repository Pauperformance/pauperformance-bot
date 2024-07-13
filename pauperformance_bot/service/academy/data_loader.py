import os
import re
from os import path
from typing import List, Optional

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


class AcademyDataLoader:
    """Service to load in memory all the Academy assets."""

    def __init__(self, academy_fs=AcademyFileSystem()):
        self._academy_fs = academy_fs

    def load_classified_decks(self, archetype: str) -> List[PlayableDeck]:
        """Returns a list of decks for the given archetype."""
        deck_dir = posix_path(self._academy_fs.ASSETS_DATA_INTEL_DECK_DIR, archetype)
        if not path.exists(deck_dir):
            logger.error(
                f"No dir for archetype {archetype} found in "
                + f"{self._academy_fs.ASSETS_DATA_INTEL_DECK_DIR}"
            )
            return []
        playable_decks, missing = self.__load_all(deck_dir)
        if missing:
            logger.warning(
                f"{len(missing)} decks not found in "
                + f"{self._academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR} "
                + f"for archetype {archetype}: {missing}"
            )
        return playable_decks

    @staticmethod
    def __load_deck(playable_deck_txt) -> Optional[PlayableDeck]:
        playable_deck = None
        try:
            with open(playable_deck_txt) as playable_f:
                lines = [line.strip() for line in playable_f.readlines()]
                playable_deck = parse_playable_deck_from_lines(lines)
        except Exception as e:
            logger.error(f"Cannot parse {playable_deck_txt}. Error: {e}")
        finally:
            return playable_deck

    def __load_all(self, deck_dir):
        missing = []
        playable_decks = []
        for deck_file in os.listdir(deck_dir):
            with open(posix_path(deck_dir, deck_file)) as deck_f:
                deck: Deck = jsonpickle.decode(deck_f.read(), safe=True)
                deck_id = re.sub(r"^.*/", "", deck.url)
            playable_deck_txt = posix_path(
                self._academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                f"{deck_id}.txt",
            )
            if not path.exists(playable_deck_txt):
                missing.append(deck_id)
                continue
            playable = AcademyDataLoader.__load_deck(playable_deck_txt)
            if playable:
                playable_decks.append(playable)
        return playable_decks, missing
