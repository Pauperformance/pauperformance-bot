import os

from pauperformance_bot.constant.myr import TOP_PATH
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.web_page import WebPage

# ACADEMY_PATH must resolve to the top directory of the website
# (i.e. the cloned twin repo), for example:
# /home/you/Pauperformance.github.io
ACADEMY_PATH = os.getenv(
    "ACADEMY_PATH",
    posix_path(TOP_PATH.parent.as_posix(), "Pauperformance.github.io"),
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
PAUPER_POOL_OUTPUT_FILE = posix_path(
    PAGES_DIR, PAUPER_POOL_PAGE_NAME.as_markdown()
)
SET_INDEX_PAGE_NAME = WebPage("set_index")
SET_INDEX_OUTPUT_FILE = posix_path(
    PAGES_DIR, SET_INDEX_PAGE_NAME.as_markdown()
)

ARCHETYPES_DIR_RELATIVE_URL = posix_path("archetypes")
FAMILIES_DIR_RELATIVE_URL = posix_path("families")
RESOURCES_IMAGES_MANA_RELATIVE_URL = posix_path("resources", "images", "mana")
