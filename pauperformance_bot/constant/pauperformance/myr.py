import os
from pathlib import Path

from pauperformance_bot.util.path import posix_path

APPLICATION_NAME = "pauperformance-bot"
PAUPERFORMANCE_BOT_DIR = posix_path(
    Path.home().as_posix(), ".pauperformance"
)  # for user data
SECRETS_UNTRACKED_FILE = "pauperformance_bot.p13_secrets.py"
HOME_CACHE_DIR = posix_path(Path.home().as_posix(), ".cache", "pauperformance")

# Local storage
STORAGE_DIR = posix_path(PAUPERFORMANCE_BOT_DIR, "storage")
STORAGE_DECKS_SUBDIR = "decks"
STORAGE_DECKSTATS_DECKS_SUBDIR = "deckstats"
STORAGE_MTGGOLDFISH_DECKS_SUBDIR = "mtggoldfish"
STORAGE_VIDEOS_SUBDIR = "videos"
STORAGE_YOUTUBE_VIDEOS_SUBDIR = "youtube"

# Local archive
ARCHIVE_DIR = posix_path(PAUPERFORMANCE_BOT_DIR, "archive")
MTGGOLDFISH_ARCHIVE_SUBDIR = "mtggoldfish"

# TOP_PATH must resolve to the top directory (i.e. the cloned repo),
# for example:
# /home/you/pauperformance-bot
TOP_PATH = Path(__file__).parent.parent.parent.parent.resolve()
SOURCE_DIR = posix_path(TOP_PATH.as_posix(), "pauperformance_bot")

# logging
DEFAULT_LOGGING_FILE = posix_path(PAUPERFORMANCE_BOT_DIR, "pauperformance.log")
DEFAULT_DATE_FORMAT = "%Y-%m-%d, %H:%M:%S"  # allows chronological sorting
USA_DATE_FORMAT = "%Y-%m-%d"

# resources/
# | cache/
# | config/
# | silver/
# | templates/
# | last_set_index.pkl

# Use the following to check if running in GitHub (take into account possible venvs):
# from distutils.util import strtobool
# if "pythonLocation" in os.environ and strtobool(
#     os.environ.get("GITHUB_ACTIONS", "false")
# ):  # running in GitHub
#     RESOURCES_DIR = posix_path(os.getenv("pythonLocation"), "SOME/THING/")

if (
    "VIRTUAL_ENV" in os.environ and "PYCHARM_HOSTED" not in os.environ
):  # running in venv, outside PyCharm
    RESOURCES_DIR = posix_path(os.getenv("VIRTUAL_ENV", ""), "resources")
else:
    RESOURCES_DIR = posix_path(TOP_PATH.as_posix(), "resources")

CACHE_DIR = posix_path(RESOURCES_DIR, "cache")
PAUPER_CARDS_INDEX_CACHE_DIR = posix_path(CACHE_DIR, "cards_index")
DECKSTATS_DECKS_CACHE_DIR = posix_path(CACHE_DIR, "deckstats_decks")
SCRYFALL_CARDS_CACHE_DIR = posix_path(CACHE_DIR, "scryfall_cards")

CONFIG_DIR = posix_path(RESOURCES_DIR, "config")
CONFIG_ARCHETYPES_DIR = posix_path(CONFIG_DIR, "archetypes")
CONFIG_FAMILIES_DIR = posix_path(CONFIG_DIR, "families")
CONFIG_CREATORS_DIR = posix_path(CONFIG_DIR, "creators")
CONFIG_NEWSPAUPER_FILE = "newspauper.ini"

SET_INDEX_FILE = posix_path(RESOURCES_DIR, "set_index.json")


class MyrFileSystem:
    def __init__(
        self,
        root_dir: str = TOP_PATH.as_posix(),
        resources_dir: str = RESOURCES_DIR,
    ):
        self.ROOT_DIR: str = root_dir

        self.SOURCE_DIR: str = posix_path(self.ROOT_DIR, "pauperformance_bot")

        self.RESOURCES_DIR: str = resources_dir
        self.RESOURCES_CACHE_DIR: str = posix_path(self.RESOURCES_DIR, "cache")

        self.RESOURCES_CONFIG_DIR: str = posix_path(self.RESOURCES_DIR, "config")
        self.RESOURCES_CONFIG_ARCHETYPES_DIR: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "archetypes"
        )
        self.RESOURCES_CONFIG_CREATORS_DIR: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "creators"
        )
        self.RESOURCES_CONFIG_FAMILIES_DIR: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "families"
        )
        self.RESOURCES_CONFIG_VIDEOS_DIR: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "videos"
        )
        self.RESOURCES_CONFIG_NEWSPAUPER: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "newspauper.ini"
        )
        self.RESOURCES_CONFIG_CHANGELOG: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "changelog.ini"
        )
        self.RESOURCES_JSON_TIMELINE: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "timeline.json"
        )
        self.VIDEO_BANNED_IDS: str = posix_path(
            self.RESOURCES_CONFIG_VIDEOS_DIR, "video_banned_ids.txt"
        )
        self.VIDEO_BANNED_KEYWORDS: str = posix_path(
            self.RESOURCES_CONFIG_VIDEOS_DIR, "video_banned_keywords.txt"
        )
        self.VIDEO_LANGUAGES: str = posix_path(
            self.RESOURCES_CONFIG_VIDEOS_DIR, "video_languages.csv"
        )
        self.RESOURCES_SILVER_DIR: str = posix_path(self.RESOURCES_DIR, "silver")
        self.RESOURCES_SILVER_TRAINING_DATA_ARCHETYPES_DIR: str = posix_path(
            self.RESOURCES_SILVER_DIR, "training_data_archetypes"
        )
        self.MTGGOLDFISH_DECK_TRAINING_DATA: str = posix_path(
            self.RESOURCES_SILVER_TRAINING_DATA_ARCHETYPES_DIR,
            "mtggoldfish_tournament_decks.csv",
        )
        self.DPL_DECK_TRAINING_DATA: str = posix_path(
            self.RESOURCES_SILVER_TRAINING_DATA_ARCHETYPES_DIR,
            "dpl_decks.csv",
        )
        self.VIDEO_ARCHETYPES: str = posix_path(
            self.RESOURCES_SILVER_DIR,
            "video_archetypes.csv",
        )
        self.MISSING_DECK_ARCHETYPES: str = posix_path(
            self.RESOURCES_SILVER_DIR,
            "missing_deck_archetypes.csv",
        )
        self.MISSING_VIDEO_ARCHETYPES: str = posix_path(
            self.RESOURCES_SILVER_DIR,
            "missing_video_archetypes.csv",
        )
        self.MTGGOLDFISH_DECKS_CACHE_DIR: str = posix_path(
            self.RESOURCES_CACHE_DIR, "mtggoldfish_decks"
        )


MYR_FILE_SYSTEM = MyrFileSystem()
