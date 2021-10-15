import re

import requests
from pyquery import PyQuery

from pauperformance_bot.util.request import execute_http_request
from pauperformance_bot.util.time import pretty_str


class DeckstatsDeck:
    def __init__(
        self,
        owner_id,
        owner_name,
        saved_id,
        folder_id,
        name,
        added,
        updated,
        url,
    ):
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.saved_id = saved_id
        self.folder_id = folder_id
        self.name = name
        self.added = added
        self.updated = updated
        self.url = url

    @property
    def archetype(self):
        return self.name.rsplit(" ", maxsplit=1)[0]

    @property
    def p12e_code(self):
        return self.name.rsplit(" ", maxsplit=1)[1].split(".")[0]

    @property
    def description(self):
        url = self.url
        method = requests.get
        response = execute_http_request(method, url)
        pq = PyQuery(response.content)
        description_div = pq(
            ".deck_text_editable_display_content.deck_text_display_markdown"
        )
        try:
            raw_description = str(next(description_div.items()))
            raw_description = next(
                (
                    line
                    for line in raw_description.split("\n")
                    if "</p>" in line
                )
            )
            return re.sub("<[^<]+?>", "", raw_description).rstrip()
        except StopIteration:  # no description
            return ""

    def __str__(self):
        return (
            f"owner_id: {self.owner_id}; "
            f"owner_name: {self.name}; "
            f"saved_id: {self.saved_id}; "
            f"folder_id: {self.folder_id}; "
            f"name: {self.name}; "
            f"added: {pretty_str(self.added)}; "
            f"updated: {pretty_str(self.updated)}; "
            f"url: {self.url}"
        )
