import datetime
import logging
import os
from pathlib import Path

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.tournament import Tournament
from pauperformance_bot.service.mtg.mtggoldfish import MTGGoldfish
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()
logger.setLevel(logging.DEBUG)


def check_mtg_tournament_decks_are_downloaded():
    academy_fs: AcademyFileSystem = AcademyFileSystem()
    goldfish_tournaments_dir = academy_fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DIR
    json_goldfish_decks_dir = academy_fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DECKS_DIR
    raw_goldfish_decks_dir = academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR
    for tournament_file in Path(goldfish_tournaments_dir).glob("*.json"):
        tournament: Tournament = jsonpickle.decode(open(tournament_file).read())
        for deck_id in tournament.deck_ids:
            if not os.path.exists(
                json_goldfish_decks_dir + os.path.sep + deck_id + ".json"
            ):
                print(f"Missing {deck_id}.json from tournament {tournament_file}.")
            if not os.path.exists(
                raw_goldfish_decks_dir + os.path.sep + deck_id + ".txt"
            ):
                print(f"Missing {deck_id}.txt from tournament {tournament_file}.")


if __name__ == "__main__":
    mtggoldfish = MTGGoldfish()
    # beginning = datetime.datetime(day=1, month=1, year=2011)

    # 2023 done
    # 2024 done

    mtggoldfish.download_mtggoldfish_tournaments(
        datetime.datetime(day=8, month=3, year=2025),
        datetime.datetime(day=24, month=4, year=2026),
        AcademyFileSystem(),
    )

    check_mtg_tournament_decks_are_downloaded()
