import json
from functools import partial

import requests

from pauperformance_bot.constants import SCRYFALL_API_ENDPOINT
from pauperformance_bot.util.request import execute_http_request


class Scryfall:
    def __init__(self, endpoint=SCRYFALL_API_ENDPOINT):
        self.endpoint = endpoint

    def get_sets(self):
        url = f"{self.endpoint}/sets"
        method = requests.get
        response = execute_http_request(method, url)
        return json.loads(response.content)

    def get_card_named(self, exact_card_name):
        url = f"{self.endpoint}/cards/named"
        method = requests.get
        params = {'exact': exact_card_name}
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        return json.loads(response.content)

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
