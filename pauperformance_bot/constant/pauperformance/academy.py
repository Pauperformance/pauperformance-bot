import os

from pauperformance_bot.constant.pauperformance.myr import TOP_PATH
from pauperformance_bot.util.path import posix_path

# ACADEMY_PATH must resolve to the top directory of the website
# (i.e. the cloned twin repo), for example:
# /home/you/pauperformance.github.io
ACADEMY_PATH = os.getenv(
    "ACADEMY_PATH",
    posix_path(TOP_PATH.parent.as_posix(), "pauperformance.github.io"),
)

ARCHETYPES_DIR = posix_path(ACADEMY_PATH, "archetypes")
FAMILIES_DIR = posix_path(ACADEMY_PATH, "families")
PAGES_DIR = posix_path(ACADEMY_PATH, "pages")
RESOURCES_DIR = posix_path(ACADEMY_PATH, "resources")

ARCHETYPES_DIR_RELATIVE_URL = posix_path("archetypes")
FAMILIES_DIR_RELATIVE_URL = posix_path("families")


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
        self.ASSETS_DATA_CREATOR_DIR: str = posix_path(self.ASSETS_DATA_DIR, "creator")
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
