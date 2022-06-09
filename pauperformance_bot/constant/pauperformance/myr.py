import os
from pathlib import Path

from pauperformance_bot.util.path import posix_path

APPLICATION_NAME = "pauperformance-bot"
PAUPERFORMANCE_BOT_DIR = posix_path(
    Path.home().as_posix(), ".pauperformance"
)  # for user data
SECRETS_UNTRACKED_FILE = "pauperformance_bot.secrets.py"

# Local storage
STORAGE_DIR = posix_path(PAUPERFORMANCE_BOT_DIR, "storage")
STORAGE_DECKS_SUBDIR = "decks"
STORAGE_DECKSTATS_DECKS_SUBDIR = "deckstats"
STORAGE_MTGGOLDFISH_DECKS_SUBDIR = "mtggoldfish"
STORAGE_VIDEOS_SUBDIR = "videos"
STORAGE_TWITCH_VIDEOS_SUBDIR = "twitch"
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

VIDEO_DECK_TAG = "Pauperformance: "
VIDEO_LANGUAGE_TAG = "Pauperformance language: "

# resources/
# | cache/
# | config/
# | templates/
# | last_set_index.pkl

# Use the following to check if running in GitHub (take into account possible venvs):
# from distutils.util import strtobool
# if "pythonLocation" in os.environ and strtobool(
#     os.environ.get("GITHUB_ACTIONS", "false")
# ):  # running in GitHub
#     RESOURCES_DIR = posix_path(os.getenv("pythonLocation"), "SOME/THING/")

if "VIRTUAL_ENV" in os.environ:  # running in venv
    RESOURCES_DIR = posix_path(os.getenv("VIRTUAL_ENV"), "resources")
else:
    RESOURCES_DIR = posix_path(TOP_PATH.as_posix(), "resources")

CACHE_DIR = posix_path(RESOURCES_DIR, "cache")
DECKSTATS_DECKS_CACHE_DIR = posix_path(CACHE_DIR, "deckstats_decks")
MTGGOLDFISH_DECKS_CACHE_DIR = posix_path(CACHE_DIR, "mtggoldfish_decks")
SCRYFALL_CARDS_CACHE_DIR = posix_path(CACHE_DIR, "scryfall_cards")
PAUPER_CARDS_INDEX_CACHE_FILE = posix_path(
    CACHE_DIR,
    "pauper_cards_index.pkl.tgz",
)

CONFIG_DIR = posix_path(RESOURCES_DIR, "config")
CONFIG_ARCHETYPES_DIR = posix_path(CONFIG_DIR, "archetypes")
CONFIG_FAMILIES_DIR = posix_path(CONFIG_DIR, "families")
CONFIG_PHDS_DIR = posix_path(CONFIG_DIR, "phds")
CONFIG_NEWSPAUPER_FILE = "newspauper.ini"

TEMPLATES_DIR = posix_path(RESOURCES_DIR, "templates")
TEMPLATES_ARCHETYPES_DIR = posix_path(TEMPLATES_DIR, "archetypes")
ARCHETYPE_TEMPLATE_FILE = "archetype.md.j2"
TEMPLATES_FAMILIES_DIR = posix_path(TEMPLATES_DIR, "families")
FAMILY_TEMPLATE_FILE = "family.md.j2"
TEMPLATES_PAGES_DIR = posix_path(TEMPLATES_DIR, "pages")
ARCHETYPES_INDEX_TEMPLATE_FILE = "archetypes_index.md.j2"
DEV_TEMPLATE_FILE = "dev.md.j2"
HOME_TEMPLATE_FILE = "index.md.j2"
PAUPER_POOL_TEMPLATE_FILE = "pauper_pool.md.j2"
SET_INDEX_TEMPLATE_FILE = "set_index.md.j2"

LAST_SET_INDEX_FILE = posix_path(RESOURCES_DIR, "last_set_index.json")


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
        self.RESOURCES_CONFIG_FAMILIES_DIR: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "families"
        )
        self.RESOURCES_CONFIG_PHDS_DIR: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "phds"
        )
        self.RESOURCES_CONFIG_NEWSPAUPER: str = posix_path(
            self.RESOURCES_CONFIG_DIR, "newspauper.ini"
        )


MYR_FILE_SYSTEM = MyrFileSystem()
