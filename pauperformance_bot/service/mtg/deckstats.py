import json
import pickle
from functools import partial

import requests

from pauperformance_bot.constant.deckstats import (
    API_ENDPOINT,
    MONITORED_PAUPERFORMANCE_FOLDER,
)
from pauperformance_bot.constant.myr import DECKSTATS_DECKS_CACHE_DIR
from pauperformance_bot.constant.players import PAUPERFORMANCE_PLAYER
from pauperformance_bot.entity.deck.deckstats import DeckstatsDeck
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard
from pauperformance_bot.exceptions import DeckstatsException
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.naming import is_valid_p12e_deckstats_name
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.request import execute_http_request

logger = get_application_logger()


class DeckstatsService:
    def __init__(
        self,
        owner_id=PAUPERFORMANCE_PLAYER.deckstats_id,
        endpoint=API_ENDPOINT,
    ):
        self.endpoint = endpoint
        self.owner_id = owner_id

    def list_user_folders_id(self):
        url = self.endpoint
        method = requests.get
        params = {
            "action": "user_folder_get",
            "result_type": "folder;decks;parent_tree;subfolders",
            "owner_id": self.owner_id,
            "folder_id": "0",
            "decks_page": "1",
            "response_type": "json",
        }
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        response = json.loads(response.content)
        folders = {"<root>": "0"}
        for subfolder in response["folder"]["subfolders"]:
            folders[subfolder["name"]] = str(subfolder["id"])
        return folders

    def list_public_decks_in_folder(self, owner_name, folder_id):
        url = self.endpoint
        method = requests.get
        fetched_decks = []
        decks_total = -1
        curr_page = 1
        while len(fetched_decks) != decks_total:
            params = {
                "action": "user_folder_get",
                "result_type": "folder;decks;parent_tree;subfolders",
                "owner_id": self.owner_id,
                "folder_id": folder_id,
                "decks_page": str(curr_page),
                "response_type": "json",
            }
            method = partial(method, params=params)
            response = execute_http_request(method, url)
            response = json.loads(response.content)
            decks_total = response["folder"]["decks_total"]
            if "decks" not in response["folder"]:
                continue
            for deck in response["folder"]["decks"]:
                actual_name = deck["name"]
                actual_owner = owner_name
                if owner_name == PAUPERFORMANCE_PLAYER.deckstats_name:
                    dot_tokens = deck["name"].split(".")
                    actual_name = ".".join(dot_tokens[:2])
                    actual_owner = ".".join(dot_tokens[2:])
                fetched_decks.append(
                    DeckstatsDeck(
                        owner_id=deck["owner_id"],
                        owner_name=actual_owner,
                        saved_id=deck["saved_id"],
                        folder_id=folder_id,
                        name=actual_name,
                        added=deck["added"] * 1000,
                        updated=deck["updated"] * 1000,
                        url=f"https:{deck['url_neutral']}",
                    )
                )
            curr_page += 1
        return sorted(fetched_decks, key=lambda d: d.added)

    def list_pauperformance_decks(self, owner_name):
        folders = self.list_user_folders_id()
        if MONITORED_PAUPERFORMANCE_FOLDER not in folders:
            return []
        return [
            deck
            for deck in self.list_public_decks_in_folder(
                owner_name, folders[MONITORED_PAUPERFORMANCE_FOLDER]
            )
            if is_valid_p12e_deckstats_name(deck.name)
        ]

    def get_deck(
        self,
        deck_id,
        decks_cache_dir=DECKSTATS_DECKS_CACHE_DIR,
        use_cache=True,
    ):
        if use_cache:
            try:
                with open(
                    posix_path(decks_cache_dir, f"{deck_id}.pkl"), "rb"
                ) as cache_f:
                    deck = pickle.load(cache_f)
                    logger.debug(f"Loaded deck from cache: {deck}")
                    return deck
            except FileNotFoundError:
                pass
        logger.debug("No cache found for deck.")
        url = self.endpoint
        method = requests.get
        params = {
            "action": "get_deck",
            "id_type": "saved",
            "owner_id": self.owner_id,
            "id": deck_id,
            "response_type": "json",
        }
        method = partial(method, params=params)
        response = execute_http_request(method, url)
        deck = json.loads(response.content)
        with open(
            posix_path(decks_cache_dir, f"{deck_id}.pkl"), "wb"
        ) as cache_f:
            pickle.dump(deck, cache_f)
        return deck

    def to_playable_deck(self, deckstats_deck):
        logger.info(
            f"Parsing deckstats deck {deckstats_deck['saved_id']} list..."
        )
        main_section = next(
            s for s in deckstats_deck["sections"] if s["name"] == "Main"
        )
        playable_main = []
        for c in main_section["cards"]:
            if not c["valid"]:
                raise DeckstatsException(
                    f"Invalid entry in deckstats deck "
                    f"{deckstats_deck['saved_id']} (main): "
                    f"{c['amount']} {c['name']}"
                )
            playable_main.append(PlayedCard(c["amount"], c["name"]))
        playable_sideboard = []
        for c in deckstats_deck["sideboard"]:
            if not c["valid"]:
                raise DeckstatsException(
                    f"Invalid entry in deckstats deck "
                    f"{deckstats_deck['saved_id']} (sideboard): "
                    f"{c['amount']} {c['name']}"
                )
            playable_sideboard.append(PlayedCard(c["amount"], c["name"]))
        playable_deck = PlayableDeck(playable_main, playable_sideboard)
        # logger.debug(f"Parsed deck: {playable_deck}")
        logger.info(
            f"Parsed deckstats deck {deckstats_deck['saved_id']} list."
        )
        return playable_deck
