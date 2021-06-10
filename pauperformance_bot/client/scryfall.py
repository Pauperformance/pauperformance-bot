import json
import pickle
from functools import partial

import requests

from pauperformance_bot.constants import SCRYFALL_API_ENDPOINT, \
    SCRYFALL_CARDS_CACHE_DIR
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.request import execute_http_request

logger = get_application_logger()


class Scryfall:
    def __init__(self, endpoint=SCRYFALL_API_ENDPOINT):
        self.endpoint = endpoint

    def get_sets(self):
        url = f"{self.endpoint}/sets"
        method = requests.get
        response = execute_http_request(method, url)
        return json.loads(response.content)

    def get_card_named(
            self,
            exact_card_name,
            cards_cache_dir=SCRYFALL_CARDS_CACHE_DIR,
    ):
        try:
            with open(posix_path(cards_cache_dir, f"{exact_card_name}.pkl"), "rb") as cache_f:
                card = pickle.load(cache_f)
                logger.debug(f"Loaded card from cache: {card}")
        except FileNotFoundError:
            logger.debug("No cache found for card.")
        url = f"{self.endpoint}/cards/named"
        method = requests.get
        params = {'exact': exact_card_name}
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        card = json.loads(response.content)
        with open(posix_path(cards_cache_dir, f"{exact_card_name}.pkl"), 'wb') as cache_f:
            pickle.dump(card, cache_f)
        return card

    def search_cards(self, query):
        url = f"{self.endpoint}/cards/search"
        method = requests.get
        params = {'q': query}
        method = partial(method, params=params)
        has_more = True
        cards = []
        try:
            while has_more:
                response = execute_http_request(method, url)
                response = json.loads(response.content)
                cards += response['data']
                has_more = response['has_more']
                if has_more:
                    url = response['next_page']
            return cards
        except requests.exceptions.HTTPError as exc:
            response = json.loads(exc.response.content)
            if exc.response.status_code == 404 and response['code'] == 'not_found':
                return {}

    def get_legal_lands(self, cards_cache_dir=SCRYFALL_CARDS_CACHE_DIR):
        cache_key = "all_legal_lands.pkl"
        try:
            with open(posix_path(cards_cache_dir, cache_key), "rb") as cache_f:
                lands = pickle.load(cache_f)
                logger.debug(f"Loaded lands from cache: {lands}")
        except FileNotFoundError:
            logger.debug("No cache found for lands.")
        query = "type:land legal:pauper"
        lands = self.search_cards(query)
        with open(posix_path(cards_cache_dir, cache_key), 'wb') as cache_f:
            pickle.dump(lands, cache_f)
        return lands

