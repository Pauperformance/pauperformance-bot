import json
import pickle
import urllib.parse
from functools import lru_cache, partial

import requests

from pauperformance_bot.constant.mtg.scryfall import API_ENDPOINT, WEBSITE_URL
from pauperformance_bot.constant.pauperformance.myr import SCRYFALL_CARDS_CACHE_DIR
from pauperformance_bot.exceptions import CardNotFoundException
from pauperformance_bot.util.cache import to_pkl_name
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.request import execute_http_request

logger = get_application_logger()


class ScryfallService:
    def __init__(self, website_url=WEBSITE_URL, endpoint=API_ENDPOINT):
        self.website_url = website_url
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
        fuzzy=False,
    ):
        try:
            with open(
                posix_path(cards_cache_dir, to_pkl_name(exact_card_name)), "rb"
            ) as cache_f:
                card = pickle.load(cache_f)
                logger.debug(f"Loaded card from cache: {exact_card_name}")
                # logger.debug(f"Card: {card}")
                return card
        except FileNotFoundError:
            logger.debug(f"No cache found for card {exact_card_name}.")
            url = f"{self.endpoint}/cards/named"
            method = requests.get
            if fuzzy:
                params = {"fuzzy": exact_card_name}
            else:
                params = {"exact": exact_card_name}
            method = partial(method, params=params)
            try:
                response = execute_http_request(method, url)
                card = json.loads(response.content)
                with open(
                    posix_path(cards_cache_dir, to_pkl_name(exact_card_name)), "wb"
                ) as cache_f:
                    pickle.dump(card, cache_f)
                return card
            except requests.exceptions.HTTPError as exc:
                if exc.response.status_code == 404:
                    message = f"Absent card in Scryfall: {exact_card_name}."
                    logger.error(message)
                    raise CardNotFoundException(message)
                else:
                    raise

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
            if exc.response.status_code == 404 and response["code"] == "not_found":
                return {}

    @lru_cache(maxsize=1)
    def get_legal_lands(self):
        query = "type:land legal:pauper"
        return self.search_cards(query)

    @lru_cache(maxsize=1)
    def get_legal_artifact_lands(self):
        query = "(type:artifact type:land) legal:pauper"
        return self.search_cards(query)

    @lru_cache(maxsize=1)
    def get_banned_cards(self):
        query = "banned:pauper"
        return self.search_cards(query)

    def get_artist_gallery_search_url(self, artist_name: str):
        query = f"a:'{artist_name}'"
        encoded_query = urllib.parse.quote(query)
        query_params = "&".join(("unique=art", "as=grid", "order=name"))
        return f"{self.website_url}/search?q={encoded_query}&{query_params}"

    def get_card_from_url(self, card_url: str):
        logger.debug(f"Retrieving card from url: {card_url}...")
        # make an educated guess on the card name from the URL
        card_name = card_url.split("/")[-1].replace("-", " ")
        logger.debug(f"Trying card with name: {card_name}...")
        card = self.get_card_named(card_name)
        logger.debug(f"Retrieved card from url: {card_url}.")
        return card
