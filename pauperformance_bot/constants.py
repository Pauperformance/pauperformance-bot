from pathlib import Path
from pauperformance_bot.util.path import posix_path

# pauperformance-bot constants
APPLICATION_NAME = "pauperformance-bot"
PAUPERFORMANCE_BOT_DIR = posix_path(Path.home().as_posix(), ".pauperformance")

DEFAULT_LOGGING_FILE = posix_path(PAUPERFORMANCE_BOT_DIR, "pauperformance.log")
DEFAULT_DATE_FORMAT = "%Y-%m-%d, %H:%M:%S"  # allows chronological sorting

TOP_DIR = Path(__file__).parent.parent.resolve()
SOURCE_DIR = posix_path(TOP_DIR.as_posix(), "pauperformance_bot")

DECKSTATS_PAUPERFORMANCE_FOLDER = "Pauperformance"

# pauperformance-bot resources
RESOURCES_DIR = posix_path(TOP_DIR.as_posix(), "resources")

CONFIG_DIR = posix_path(RESOURCES_DIR, "config")
CONFIG_ARCHETYPES_DIR = posix_path(CONFIG_DIR, "archetypes")
ARCHETYPE_TEMPLATE_FILE = "archetype.md.j2"

TEMPLATES_DIR = posix_path(RESOURCES_DIR, "templates")
TEMPLATES_PAGES_DIR = posix_path(TEMPLATES_DIR, "pages")
TEMPLATES_ARCHETYPES_DIR = posix_path(TEMPLATES_DIR, "archetypes")
SET_INDEX_TEMPLATE_FILE = "set_index.md.j2"


# pauperformance public repo
PAUPERFORMANCE_DIR = posix_path(TOP_DIR.parent.as_posix(), "pauperformance")
PAUPERFORMANCE_ARCHETYPES_DIR = posix_path(PAUPERFORMANCE_DIR, "archetypes")
PAUPERFORMANCE_PAGES_DIR = posix_path(PAUPERFORMANCE_DIR, "pages")
PAUPERFORMANCE_RESOURCES_DIR = posix_path(PAUPERFORMANCE_DIR, "resources")
SET_INDEX_OUTPUT_FILE = posix_path(PAUPERFORMANCE_PAGES_DIR, "set_index.md")

PAUPERFORMANCE_RESOURCES_IMAGES_MANA_RELATIVE_URL = posix_path("resources", "images", "mana")

# third-party resources
SCRYFALL_API_ENDPOINT = "https://api.scryfall.com"
DECKSTATS_API_ENDPOINT = "https://deckstats.net/api.php"
