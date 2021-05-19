from pathlib import Path

APPLICATION_NAME = "pauperformance-bot"
PAUPERFORMANCE_BOT_DIR = (Path.home() / ".pauperformance").as_posix()
DEFAULT_LOGGING_FILE = (Path(PAUPERFORMANCE_BOT_DIR) / "pauperformance.log").as_posix()

DEFAULT_DATE_FORMAT = "%Y-%m-%d, %H:%M:%S"

TOP_DIR = Path(__file__).parent.parent.resolve()

SOURCE_DIR = (TOP_DIR / "pauperformance_bot").as_posix()

RESOURCES_DIR = (TOP_DIR / "resources").as_posix()
TEMPLATES_DIR = (Path(RESOURCES_DIR) / "templates").as_posix()
SET_INDEX_TEMPLATE_FILE = "set_index.md.j2"
SET_INDEX_OUTPUT_FILE = (Path(TEMPLATES_DIR) / "set_index.md").as_posix()

SCRYFALL_API_ENDPOINT = "https://api.scryfall.com"
