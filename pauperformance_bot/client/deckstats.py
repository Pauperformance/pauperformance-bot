import json
from functools import partial

import requests

from pauperformance_bot.constants import DECKSTATS_API_ENDPOINT, DECKSTATS_PAUPERFORMANCE_FOLDER
from pauperformance_bot.entity.deckstats_deck import DeckstatsDeck
from pauperformance_bot.players import PAUPERFORMANCE_PLAYER
from pauperformance_bot.util.request import execute_http_request


class Deckstats:
    def __init__(
            self,
            endpoint=DECKSTATS_API_ENDPOINT,
            owner_id=PAUPERFORMANCE_PLAYER.deckstats_id,
    ):
        self.endpoint = endpoint
        self.owner_id = owner_id

    def list_user_folders_id(self):
        url = self.endpoint
        method = requests.get
        params = {
            'action': 'user_folder_get',
            'result_type': 'folder;decks;parent_tree;subfolders',
            'owner_id': self.owner_id,
            'folder_id': '0',
            'decks_page': '1',
            'response_type': 'json',
        }
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        response = json.loads(response.content)
        folders = {'<root>': '0'}
        for subfolder in response['folder']['subfolders']:
            folders[subfolder['name']] = str(subfolder['id'])
        return folders

    def list_public_decks_in_folder(self, owner_name, folder_id,):
        url = self.endpoint
        method = requests.get
        fetched_decks = []
        decks_total = -1
        curr_page = 1
        while len(fetched_decks) != decks_total:
            params = {
                'action': 'user_folder_get',
                'result_type': 'folder;decks;parent_tree;subfolders',
                'owner_id': self.owner_id,
                'folder_id': folder_id,
                'decks_page': str(curr_page),
                'response_type': 'json',
            }
            method = partial(method, params=params)
            response = execute_http_request(method, url)
            response = json.loads(response.content)
            decks_total = response['folder']['decks_total']
            if 'decks' not in response['folder']:
                continue
            for deck in response['folder']['decks']:
                fetched_decks.append(DeckstatsDeck(
                    owner_id=deck['owner_id'],
                    owner_name=owner_name,
                    saved_id=deck['saved_id'],
                    folder_id=folder_id,
                    name=deck['name'],
                    added=deck['added'] * 1000,
                    updated=deck['updated'] * 1000,
                    url=f"https:{deck['url_neutral']}",
                ))
            curr_page += 1
        return sorted(fetched_decks, key=lambda d: d.added)

    def list_pauperformance_decks(self, owner_name):
        folders = self.list_user_folders_id()
        if DECKSTATS_PAUPERFORMANCE_FOLDER not in folders:
            return []
        # TODO: check if name is valid
        return self.list_public_decks_in_folder(
            owner_name,
            folders[DECKSTATS_PAUPERFORMANCE_FOLDER]
        )

    def get_deck(self, deck_id):
        url = self.endpoint
        method = requests.get
        params = {
            'action': 'get_deck',
            'id_type': 'saved',
            'owner_id': self.owner_id,
            'id': deck_id,
            'response_type': 'json',
        }
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        return json.loads(response.content)

