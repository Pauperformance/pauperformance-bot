import json
import os
import uuid
from os import linesep, listdir
from os.path import isfile, join, sep

from pauperformance_bot.constant.myr import (
    STORAGE_DECKS_SUBDIR,
    STORAGE_DIR,
    STORAGE_MTGGOLDFISH_DECKS_SUBDIR,
)
from pauperformance_bot.entity.deck.archive.local import (
    LocalArchivedDeck as LocalDeck,
)
from pauperformance_bot.entity.deck.playable import (
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.mtg.archive.abstract import (
    AbstractArchiveService,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.time import now

logger = get_application_logger()


class LocalArchiveService(AbstractArchiveService):
    def __init__(
        self,
        root_dir=posix_path(
            STORAGE_DIR, STORAGE_DECKS_SUBDIR, STORAGE_MTGGOLDFISH_DECKS_SUBDIR
        ),
    ):
        self._root_dir = root_dir

    def get_uri(self, deck_id):
        return f"{self._root_dir}{sep}{deck_id}"

    def create_deck(self, name, description, playable_deck):
        deck_id = uuid.uuid4().hex
        output_file = f"{self.get_uri(deck_id)}"
        if os.path.isfile(output_file):
            raise ValueError(
                f"uuid4 name collision on {deck_id}! "
                f"Do you know how rare is this event?"
            )
        logger.info(f"Storing file {output_file}...")
        with open(output_file, "w", encoding="utf-8") as out_f:
            data = {
                "name": name,
                "creation_date": now(),
                "description": description,
                "playable_deck": str(playable_deck),
            }
            json.dump(data, out_f)
        logger.info(f"Stored file {output_file}.")
        return deck_id

    def list_decks(self, filter_name=""):
        logger.info(f"Listing decks in {self._root_dir}...")
        decks = []
        for file in (
            join(self._root_dir, f)
            for f in listdir(self._root_dir)
            if isfile(join(self._root_dir, f))
        ):
            logger.debug(f"Processing deck in {file}...")
            with open(file, "r", encoding="utf-8") as in_f:
                data = json.load(in_f)
                decks.append(
                    LocalDeck(
                        data["name"],
                        data["creation_date"],
                        file.rsplit(sep, maxsplit=1)[1],
                        self._root_dir,
                    )
                )
        logger.info(f"Listed files in {self._root_dir}...")
        return decks

    def delete_deck(self, deck_id):
        file_name = self.get_uri(deck_id)
        logger.info(f"Deleting deck {file_name}...")
        os.remove(file_name)
        logger.info(f"Deleted deck {file_name}.")

    @staticmethod
    def to_playable_deck(
        listed_deck, decks_cache_dir="USELESS!", use_cache=False
    ):
        if use_cache:
            logger.info("Ignoring cache on local Archive...")
        file = listed_deck.url
        logger.debug(f"Processing deck in {file}...")
        with open(file, "r", encoding="utf-8") as in_f:
            data = json.load(in_f)
            playable_deck_str = data["playable_deck"]
            lines = playable_deck_str.split(linesep) + [
                ""
            ]  # for consistency with the original file
            deck = parse_playable_deck_from_lines(
                [
                    line
                    for line in lines
                    if not line.endswith(":")
                    and not line.startswith("Main (")
                    and not line.startswith("Sideboard (")
                ]
            )
            return deck
