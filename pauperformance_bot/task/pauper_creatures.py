import json
import logging
from functools import partial
from time import sleep

import requests

API_ENDPOINT = "https://api.scryfall.com"
LOG_FORMAT = (
    "%(levelname)s:%(asctime)s:%(module)s:%(funcName)s:"
    "L%(lineno)d: %(message)s"
)

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger("scryfall")


def execute_http_request(request_fn, url, timeout=(3 * 20, 120)):
    # Assumes the request_fn is from requests module.
    # Timeout is a tuple (connection_timeout, read_timeout).
    # Further details here:
    # https://3.python-requests.org/user/quickstart/#timeouts
    response = request_fn(url, timeout=timeout)
    response.raise_for_status()
    return response


class ScryfallService:
    def __init__(self, endpoint=API_ENDPOINT):
        self.endpoint = endpoint

    def get_card_named(self, exact_card_name):
        url = f"{self.endpoint}/cards/named"
        method = requests.get
        params = {"exact": exact_card_name}
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        return json.loads(response.content)

    def search_cards(self, query):
        url = f"{self.endpoint}/cards/search"
        method = requests.get
        params = {"q": query}
        method = partial(method, params=params)
        has_more = True
        cards = []
        try:
            while has_more:
                response = execute_http_request(method, url)
                response = json.loads(response.content)
                cards += response["data"]
                has_more = response["has_more"]
                if has_more:
                    url = response["next_page"]
            return cards
        except requests.exceptions.HTTPError as exc:
            response = json.loads(exc.response.content)
            if (
                exc.response.status_code == 404
                and response["code"] == "not_found"
            ):
                return {}


def pauper_only_creatures():
    scryfall = ScryfallService()
    pauper_creatures = scryfall.search_cards("type:creature legal:pauper")
    all_creatures_types = set()
    for card in pauper_creatures:
        type_line = card["type_line"]
        # deal with "double" cards
        # (e.g. Delver of Secrets // Insectile Aberration)
        for half in type_line.split("//"):
            if "Creature" not in half:
                continue  # ignore non-creature half
            subtypes = half.split(" — ")[1]  # discard type and keep subtypes
            for subtype in subtypes.split(" "):  # possibly multiple subtypes
                if subtype == "":  # deal with Scryfall's trailing whitespace
                    continue
                all_creatures_types.add(subtype)
    print(all_creatures_types)
    only_common = []
    for creature_type in all_creatures_types:
        non_common = scryfall.search_cards(
            f"(type:creature type:{creature_type}) "
            f"(rarity:u OR rarity:r OR rarity:m)"
        )
        if len(non_common) == 0:
            only_common.append(creature_type)
            print(f"Only at common: {creature_type}")
        sleep(0.2)  # do not flood Scryfall back end
    print(sorted(only_common))


if __name__ == "__main__":
    pauper_only_creatures()
