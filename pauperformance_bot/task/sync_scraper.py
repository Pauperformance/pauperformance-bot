import datetime
import logging
import os
from pathlib import Path

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.tournament import Tournament
from pauperformance_bot.service.mtg.mtggoldfish import MTGGoldfish
from pauperformance_bot.service.pauperformance.silver.sideboard_scraper import (
    update_sideboard_guides,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import last_n_weeks

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


def download_mtggoldfish(since):
    mtggoldfish = MTGGoldfish()
    # You can download a custom range of tournaments building datetime objects via e.g.
    # datetime.datetime(day=18, month=5, year=2026)
    # datetime.datetime(day=26, month=5, year=2026)
    mtggoldfish.download_mtggoldfish_tournaments(
        datetime.datetime.fromtimestamp(since / 1000),
        datetime.datetime.now(),
        AcademyFileSystem(),
    )
    check_mtg_tournament_decks_are_downloaded()


def scrape(since):
    download_mtggoldfish(since)
    update_sideboard_guides()


if __name__ == "__main__":
    # scrape(last_week())
    scrape(last_n_weeks(4 * 12))
