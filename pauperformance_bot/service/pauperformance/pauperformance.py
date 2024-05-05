import collections
import glob
import json
import os
from datetime import datetime
from pathlib import Path
from time import sleep

from constant.mtg.scryfall import REQUESTS_SLEEP_SECONDS
from requests.exceptions import HTTPError

import pauperformance_bot
from pauperformance_bot.constant.arena.twitch import TWITCH_VIDEO_URL
from pauperformance_bot.constant.arena.youtube import YOUTUBE_VIDEO_URL
from pauperformance_bot.constant.pauperformance.myr import (
    CONFIG_ARCHETYPES_DIR,
    CONFIG_FAMILIES_DIR,
    PAUPER_CARDS_INDEX_CACHE_DIR,
    SET_INDEX_FILE,
    USA_DATE_FORMAT,
)
from pauperformance_bot.constant.pauperformance.pauperformance import (
    INCREMENTAL_CARDS_INDEX_SKIP_SETS,
    KNOWN_SETS_WITH_NO_PAUPER_CARDS,
)
from pauperformance_bot.entity.academy_video import AcademyVideo
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.service.arena.twitch import TwitchService
from pauperformance_bot.service.arena.youtube import YouTubeService
from pauperformance_bot.service.mtg.deckstats import DeckstatsService
from pauperformance_bot.service.mtg.scryfall import ScryfallService
from pauperformance_bot.service.nexus.sync.messages_sender import (
    DiscordMessagesSenderSyncService,
)
from pauperformance_bot.service.pauperformance.archive.abstract import (
    AbstractArchiveService,
)
from pauperformance_bot.service.pauperformance.config_reader import ConfigReader
from pauperformance_bot.service.pauperformance.storage.abstract import (
    AbstractStorageService,
)
from pauperformance_bot.util.config import read_archetype_config
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


class PauperformanceService:
    def __init__(
        self,
        storage,
        archive,
        scryfall=ScryfallService(),
        twitch=TwitchService(),
        youtube=YouTubeService(),
        config_reader=ConfigReader(),
    ):
        self.storage: AbstractStorageService = storage
        self.archive: AbstractArchiveService = archive
        self.scryfall = scryfall
        self.twitch = twitch
        self.youtube = youtube
        self.config_reader = config_reader
        self.players = config_reader.list_phds()
        self.set_index = self._build_set_index()
        self.card_index = self._build_card_index()
        self.incremental_card_index = self._build_incremental_card_index()

    def _build_set_index(self, set_index_file=SET_INDEX_FILE):
        try:
            logger.info("Building Scryfall set index...")
            scryfall_sets = self.scryfall.get_sets()
            scryfall_sets = sorted(
                scryfall_sets["data"], key=lambda s: s["released_at"] + s["code"]
            )
            logger.info("Built Scryfall set index.")
        except HTTPError:  # Scryfall may be unreachable
            logger.warning(
                "Unable to retrieve Scryfall sets. Going to use cached version."
            )
            scryfall_sets = []

        logger.info("Building Pauperformance set index...")
        with open(set_index_file, "r") as index_f:
            content_str = index_f.read()
            json_set_index = json.loads(
                content_str,
                object_pairs_hook=collections.OrderedDict,
            )
        set_index = collections.OrderedDict(
            {int(k): dict(v) for k, v in json_set_index.items()}
        )
        known_sets = {s["scryfall_code"] for s in set_index.values()}
        p12e_code = max(set_index.keys()) + 1
        need_to_update_file = False
        for s in scryfall_sets:
            if s["code"] in known_sets:
                continue
            set_index[p12e_code] = {
                "p12e_code": p12e_code,
                "scryfall_code": s["code"],
                "name": s["name"],
                "date": s["released_at"],
            }
            need_to_update_file = True
            p12e_code += 1
        logger.info("Built Pauperformance set index.")

        if need_to_update_file:
            logger.info("Saving Pauperformance set index...")
            with open(set_index_file, "w") as index_f:
                index_f.write(json.dumps(set_index, indent=4))
            logger.info("Saved Pauperformance set index.")
        return set_index

    def _build_card_index(
        self,
        skip_sets=KNOWN_SETS_WITH_NO_PAUPER_CARDS,
        cards_index_cache_dir=PAUPER_CARDS_INDEX_CACHE_DIR,
    ):
        card_index = {}
        os.makedirs(cards_index_cache_dir, exist_ok=True)
        for item in self.set_index.values():
            p12e_code = item["p12e_code"]
            if p12e_code in skip_sets:
                card_index[p12e_code] = []
                continue
            set_cache_file = posix_path(cards_index_cache_dir, f"{p12e_code}.json")
            set_index = []
            try:
                with open(set_cache_file, "r") as cache_f:
                    set_index = json.load(cache_f)
                    logger.debug(
                        f"Loaded set index from cache: {set_cache_file} "
                        f"({len(set_index)} cards)."
                    )
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                logger.debug(f"Missing cache for set {p12e_code}: querying Scryfall...")
                scryfall_code = item["scryfall_code"]
                query = f"set:{scryfall_code} rarity:common legal:pauper"
                set_index = self.scryfall.search_cards(query)
                if len(set_index) > 0:
                    with open(set_cache_file, "w") as cache_f:
                        json.dump(set_index, cache_f)
                        logger.debug(
                            f"Saved set index to cache: {set_cache_file} "
                            f"({len(set_index)} cards)."
                        )
                sleep(REQUESTS_SLEEP_SECONDS)
            finally:
                card_index[p12e_code] = set_index
        useless_sets = set(i for i in card_index if len(card_index[i]) == 0)
        to_be_removed_sets = useless_sets - set(KNOWN_SETS_WITH_NO_PAUPER_CARDS)
        if len(to_be_removed_sets) > 0:
            constant_module = pauperformance_bot.__path__[0]
            constant_file = (
                pauperformance_bot.constant.pauperformance.pauperformance.__file__
            )
            constant_relative_path = constant_file[len(constant_module) + 1 :]
            logger.warning(
                f"Please, update the list of known sets with no pauper cards "
                f"({constant_relative_path}) "
                f"adding: {sorted(list(to_be_removed_sets))}"
            )

        return card_index

    def _build_incremental_card_index(
        self,
        skip_sets=INCREMENTAL_CARDS_INDEX_SKIP_SETS,
    ):
        incremental_card_index = {}
        existing_card_names = set()
        useless_sets = set()
        for p12e_code, cards in self.card_index.items():
            logger.debug(f"Processing set with p12e_code: {p12e_code}...")

            if (
                p12e_code in skip_sets
                or "Promos" in self.set_index[p12e_code]["name"]
                or "Black Border" in self.set_index[p12e_code]["name"]
            ):
                logger.debug(f"Skipping set {self.set_index[p12e_code]['name']}...")
                incremental_card_index[p12e_code] = []
                useless_sets.add(p12e_code)
                continue

            new_cards = []
            for card in cards:
                if card["name"] in existing_card_names:
                    continue
                new_cards.append(card)
                existing_card_names.add(card["name"])
            incremental_card_index[p12e_code] = new_cards
            logger.debug(f"Found {len(new_cards)} new cards.")
        to_be_removed_sets = useless_sets - set(INCREMENTAL_CARDS_INDEX_SKIP_SETS)
        if len(to_be_removed_sets) > 0:
            constant_module = pauperformance_bot.__path__[0]
            constant_file = (
                pauperformance_bot.constant.pauperformance.pauperformance.__file__
            )
            constant_relative_path = constant_file[len(constant_module) + 1 :]
            logger.warning(
                f"Please, update the list of known sets to be skipped for the "
                f"incremental cards index ({constant_relative_path}) adding: "
                f"{sorted(list(to_be_removed_sets))}"
            )
        return incremental_card_index

    def list_deckstats_decks(self):
        all_decks = []
        for player in self.players:
            if not player.deckstats_id:
                logger.info(
                    f"Skipping player {player.name} with no Deckstats account..."
                )
                continue
            logger.info(f"Processing player {player.name}...")
            deckstats = DeckstatsService(owner_id=player.deckstats_id)
            player_decks = deckstats.list_pauperformance_decks(player.deckstats_name)
            logger.info(f"Found {len(player_decks)} decks.")
            all_decks += player_decks
        all_decks.sort(reverse=True, key=lambda d: d.p12e_code)
        archetypes = self.get_archetypes()
        for deck in all_decks:
            if deck.archetype not in archetypes:
                logger.warning(
                    f"Deck {deck.name} by {deck.owner_name} doesn't match any "
                    f"known archetype."
                )
        return all_decks

    def list_archived_decks(self) -> list[AbstractArchivedDeck]:
        return self.archive.list_decks()

    @staticmethod
    def get_archetypes(config_pages_dir=CONFIG_ARCHETYPES_DIR):
        return set(
            Path(a).name.replace(".ini", "")
            for a in glob.glob(f"{config_pages_dir}/*.ini")
        )

    @staticmethod
    def get_families(config_pages_dir=CONFIG_FAMILIES_DIR):
        return set(
            Path(a).name.replace(".ini", "")
            for a in glob.glob(f"{config_pages_dir}/*.ini")
        )

    def analyze_cards_frequency(self, archetype_decks):
        if len(archetype_decks) < 2:
            return [], []
        lands = set(land["name"] for land in self.scryfall.get_legal_lands())
        decks_cards = {}
        all_cards = set()
        for deck in archetype_decks:
            playable_deck = self.archive.to_playable_deck(deck)
            cards = [c.card_name for c in playable_deck.mainboard]
            decks_cards[deck.deck_id] = cards
            all_cards.update(cards)
        staples = set(all_cards)
        for deck_list in decks_cards.values():
            staples = staples & set(deck_list)
        staples = staples - lands
        frequents = all_cards - staples - lands
        return list(staples), list(frequents)

    def get_set_index_by_date(self, usa_date):
        logger.debug(f"Getting set index for USA date {usa_date}")
        return [
            s
            for s in self.set_index.values()
            if s["date"] <= usa_date
            and len(self.incremental_card_index.get(s["p12e_code"])) > 0
        ][-1]

    def get_current_set_index(self):
        return self.get_set_index_by_date(datetime.today().strftime(USA_DATE_FORMAT))

    def delete_deck(self, deck_name):
        # a deck needs to be deleted both from the archive and from the storage
        archived_deck_id = None
        for deck in self.list_archived_decks():
            if deck.p12e_name != deck_name:
                continue
            archived_deck_id = deck.deck_id
            break
        if archived_deck_id is None:
            raise PauperformanceException(
                f"Unable to find archived deck with name {deck_name}"
            )
        # remove from archive
        logger.debug(f"Deleting archived deck with id {archived_deck_id}...")
        self.archive.delete_deck(archived_deck_id)
        logger.debug(f"Deleted archived deck with id {archived_deck_id}.")
        # remove from storage
        logger.debug(f"Deleting stored deck with name {deck_name}...")
        self.storage.delete_deck_by_name(deck_name)
        message = f"Deleted stored deck with name {deck_name}."
        logger.info(message)
        discord_logger = DiscordMessagesSenderSyncService([message])
        discord_logger.run_task()

    def _list_twitch_videos(self):
        logger.debug("Retrieving stored Twitch videos...")
        academy_videos = []
        for video in self.storage.list_imported_twitch_videos():
            video_id, user_name, language, date, key = video.split(">")
            video_path = posix_path(
                self.storage.youtube_video_path,
                video + ".txt",  # TODO: get rid of this
            )
            indexable_video = self.storage.get_file(video_path)
            academy_videos.append(
                AcademyVideo(
                    video_id,
                    user_name,
                    indexable_video["title"],
                    language,
                    date,
                    indexable_video["deck_name"],
                    indexable_video["archetype"],
                    indexable_video["phd"],
                    f"{TWITCH_VIDEO_URL}{video_id}",
                    "twitch",
                )
            )
        logger.debug("Retrieved stored Twitch videos.")
        return academy_videos

    def _list_youtube_videos(self):
        logger.debug("Retrieving stored YouTube videos...")
        academy_videos = []
        for video in self.storage.list_imported_youtube_videos():
            video_id, user_name, language, date, key = video.split(">")
            video_path = posix_path(
                self.storage.youtube_video_path,
                video + ".txt",  # TODO: get rid of this
            )
            indexable_video = self.storage.get_file(video_path)
            academy_videos.append(
                AcademyVideo(
                    video_id,
                    user_name,
                    indexable_video["title"],
                    language,
                    date,
                    indexable_video["deck_name"],
                    indexable_video["archetype"],
                    indexable_video["phd"],
                    f"{YOUTUBE_VIDEO_URL}{video_id}",
                    "youtube",
                )
            )
        logger.debug("Retrieved stored YouTube videos.")
        return academy_videos

    def list_videos(self) -> list[AcademyVideo]:
        return self._list_twitch_videos() + self._list_youtube_videos()

    def print_stats(
        self,
        archetypes_config_dir=CONFIG_ARCHETYPES_DIR,
    ):
        print(f"PhDs: {len(self.players) - 1}")
        print(f"Archetypes: {len(self.get_archetypes())}")
        print(f"Families: {len(self.get_families())}")
        resources = 0
        for archetype_config_file in glob.glob(f"{archetypes_config_dir}/*.ini"):
            config = read_archetype_config(archetype_config_file)
            resources += len(config["resources"])
        print(f"Resources: {resources}")
        print(f"Decks: {len(self.list_archived_decks())}")
        print(f"Videos: {len(self.list_videos())}")

    def get_playable_deck(self, deck_name: str) -> PlayableDeck:
        return self.archive.to_playable_deck(self.archive.get_deck(deck_name))
