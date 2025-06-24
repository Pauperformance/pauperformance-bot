import os

from pauperformance_bot.constant.pauperformance.myr import TOP_PATH
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.web_page import WebPage

# ACADEMY_PATH must resolve to the top directory of the website
# (i.e. the cloned twin repo), for example:
# /home/you/pauperformance.github.io
ACADEMY_PATH = os.getenv(
    "ACADEMY_PATH",
    posix_path(TOP_PATH.parent.as_posix(), "pauperformance.github.io"),
)

HOME_PAGE_NAME = WebPage("index")
HOME_OUTPUT_FILE = posix_path(ACADEMY_PATH, HOME_PAGE_NAME.as_markdown())

ARCHETYPES_DIR = posix_path(ACADEMY_PATH, "archetypes")
FAMILIES_DIR = posix_path(ACADEMY_PATH, "families")
PAGES_DIR = posix_path(ACADEMY_PATH, "pages")
RESOURCES_DIR = posix_path(ACADEMY_PATH, "resources")

ARCHETYPES_INDEX_PAGE_NAME = WebPage("archetypes_index")
ARCHETYPES_INDEX_OUTPUT_FILE = posix_path(
    PAGES_DIR, ARCHETYPES_INDEX_PAGE_NAME.as_markdown()
)
DEV_PAGE_NAME = WebPage("dev")
DEV_OUTPUT_FILE = posix_path(PAGES_DIR, DEV_PAGE_NAME.as_markdown())
PAUPER_POOL_PAGE_NAME = WebPage("pauper_pool")
PAUPER_POOL_OUTPUT_FILE = posix_path(PAGES_DIR, PAUPER_POOL_PAGE_NAME.as_markdown())
SET_INDEX_PAGE_NAME = WebPage("set_index")
SET_INDEX_OUTPUT_FILE = posix_path(PAGES_DIR, SET_INDEX_PAGE_NAME.as_markdown())

ARCHETYPES_DIR_RELATIVE_URL = posix_path("archetypes")
FAMILIES_DIR_RELATIVE_URL = posix_path("families")
RESOURCES_IMAGES_MANA_RELATIVE_URL = posix_path("resources", "images", "mana")


class AcademyFileSystem:
    def __init__(self, root_dir=ACADEMY_PATH):
        self.ROOT_DIR: str = root_dir
        self.ASSETS_DIR: str = posix_path(self.ROOT_DIR, "assets")
        self.ASSETS_DATA_DIR: str = posix_path(self.ASSETS_DIR, "data")
        self.ASSETS_DATA_ARCHETYPE_DIR: str = posix_path(
            self.ASSETS_DATA_DIR, "archetype"
        )
        self.ASSETS_DATA_DECK_DIR: str = posix_path(self.ASSETS_DATA_DIR, "deck")
        self.ASSETS_DATA_DECK_ACADEMY_DIR: str = posix_path(
            self.ASSETS_DATA_DECK_DIR, "academy"
        )
        self.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR: str = posix_path(
            self.ASSETS_DATA_DECK_DIR, "mtggoldfish_tournament"
        )
        self.ASSETS_DATA_DECK_DPL_DIR: str = posix_path(
            self.ASSETS_DATA_DECK_DIR, "dpl"
        )
        self.ASSETS_DATA_INTEL_DIR: str = posix_path(self.ASSETS_DATA_DIR, "intel")
        self.ASSETS_DATA_INTEL_DECK_DIR: str = posix_path(
            self.ASSETS_DATA_INTEL_DIR, "deck"
        )
        self.ASSETS_DATA_INTEL_CARD_DIR: str = posix_path(
            self.ASSETS_DATA_INTEL_DIR, "card"
        )
        self.ASSETS_DATA_PHD_DIR: str = posix_path(self.ASSETS_DATA_DIR, "phd")
        self.ASSETS_DATA_TOURNAMENT_DIR: str = posix_path(
            self.ASSETS_DATA_DIR, "tournament"
        )
        self.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DIR: str = posix_path(
            self.ASSETS_DATA_TOURNAMENT_DIR, "mtggoldfish"
        )
        self.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DECKS_DIR: str = posix_path(
            self.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DIR, "deck"
        )
        self.ASSETS_DATA_VIDEO_DIR: str = posix_path(self.ASSETS_DATA_DIR, "video")


ACADEMY_FILE_SYSTEM = AcademyFileSystem()
TOP_N_ARCHETYPES_PIE_CHART = 14
