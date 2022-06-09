API_ENDPOINT = "https://www.mtggoldfish.com"
DECK_API_TOKEN = "deck"
DECK_API_ENDPOINT = f"{API_ENDPOINT}/{DECK_API_TOKEN}"
DECK_DOWNLOAD_API_ENDPOINT = f"{API_ENDPOINT}/{DECK_API_TOKEN}/download"

MTGGOLDFISH_DECK_PAGE_DATE_FORMAT = "%b %d, %Y"
MTGGOLDFISH_EVENT_LINE_TEXT = "Event: "
MTGGOLDFISH_DECK_DATE_TEXT = "Deck Date: "

FULL_PAUPER_METAGAME_URL = f"{API_ENDPOINT}/metagame/pauper/full"
METAGAME_SHARE_CLASS = ".metagame-percentage"
METAGAME_ARCHETYPE_TITLE_URL_CLASS = ".archetype-tile-image a"
DECK_TOOLS_CONTAINER_CLASS = ".tools-container a"

NO_COOKIE_HEADER = {
    "accept": "text/html,application/xhtml+xml,application/xml;"
    "q=0.9,image/avif,image/webp,image/apng,*/*;"
    "q=0.8,application/signed-exchange;"
    "v=b3;"
    "q=0.9",
}
