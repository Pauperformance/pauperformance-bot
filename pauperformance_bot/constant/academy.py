from pauperformance_bot.constant.myr import TOP_PATH
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.web_page import WebPage

# ACADEMY_PATH must resolve to the top directory of the website (i.e. the cloned twin repo),
# for example /home/you/Pauperformance.github.io
ACADEMY_PATH = posix_path(TOP_PATH.parent.as_posix(), "Pauperformance.github.io")

ARCHETYPES_DIR = posix_path(ACADEMY_PATH, "archetypes")
PAGES_DIR = posix_path(ACADEMY_PATH, "pages")
RESOURCES_DIR = posix_path(ACADEMY_PATH, "resources")

PAUPER_POOL_PAGE_NAME = WebPage("pauper_pool")
PAUPER_POOL_OUTPUT_FILE = posix_path(PAGES_DIR, PAUPER_POOL_PAGE_NAME.as_markdown())
ARCHETYPES_INDEX_PAGE_NAME = WebPage("archetypes_index")
SET_INDEX_PAGE_NAME = WebPage("set_index")
ARCHETYPES_INDEX_OUTPUT_FILE = posix_path(PAGES_DIR, ARCHETYPES_INDEX_PAGE_NAME.as_markdown())
SET_INDEX_OUTPUT_FILE = posix_path(PAGES_DIR, SET_INDEX_PAGE_NAME.as_markdown())

ARCHETYPES_DIR_RELATIVE_URL = posix_path("archetypes")
RESOURCES_IMAGES_MANA_RELATIVE_URL = posix_path("resources", "images", "mana")
