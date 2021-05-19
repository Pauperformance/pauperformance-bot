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
