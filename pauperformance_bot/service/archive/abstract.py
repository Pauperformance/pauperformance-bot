import json
import time
from abc import ABCMeta, abstractmethod
from datetime import datetime
from urllib.request import urlopen

from bs4 import BeautifulSoup

from pauperformance_bot.constant.deckstats import REQUEST_SLEEP_TIMEOUT
from pauperformance_bot.constant.discord import (
    DISCORD_MYR_REACTION_KO,
    DISCORD_MYR_REACTION_OK,
    DISCORD_MYR_REACTION_SEEN,
    DISCORD_MYR_REACTION_WARNING,
)
from pauperformance_bot.constant.mtggoldfish import (
    MTGGOLDFISH_DECK_DATE_TEXT,
    MTGGOLDFISH_DECK_PAGE_DATE_FORMAT,
    MTGGOLDFISH_EVENT_LINE_TEXT,
)
from pauperformance_bot.constant.myr import USA_DATE_FORMAT
from pauperformance_bot.constant.phds import PAUPERFORMANCE
from pauperformance_bot.entity.deck.archive.mtggoldfish import MTGGoldfishArchivedDeck
from pauperformance_bot.entity.deck.playable import parse_playable_deck_from_lines
from pauperformance_bot.entity.phd import PhD
from pauperformance_bot.service.mtg.deckstats import DeckstatsService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.naming import is_valid_p12e_deckstats_name
from pauperformance_bot.util.time import datetime_to_ms, now_utc, pretty_str

logger = get_application_logger()


class AbstractArchiveService(metaclass=ABCMeta):
    @abstractmethod
    def get_uri(self, deck_id):
        pass

    @abstractmethod
    def create_deck(self, name, description, playable_deck):
        pass

    @abstractmethod
    def list_decks(self, filter_name=""):
        pass

    @abstractmethod
    def delete_deck(self, deck_id):
        pass

    @staticmethod
    @abstractmethod
    def to_playable_deck(listed_deck, decks_cache_dir=None, use_cache=True):
        pass

    async def import_player_decks_from_deckstats(
        self,
        player,
        storage,
        players_by_deckstats_id,
        set_index,
        discord,
        warning_player=PAUPERFORMANCE,
        send_notification=True,
    ):  # TODO: get rid of players_by_deckstats_id
        logger.info(f"Updating archive decks for {player.name}...")
        deckstats = DeckstatsService(owner_id=player.deckstats_id)
        imported_deckstats_deck = storage.list_imported_deckstats_deck_ids()
        for deckstats_deck in deckstats.list_pauperformance_decks(
            player.deckstats_name
        ):
            logger.debug(
                f"Processing deck '{deckstats_deck.name}' "
                f"({deckstats_deck.saved_id}) "
                f"from {deckstats_deck.owner_name}, "
                f"uploaded by "
                f"{players_by_deckstats_id[deckstats_deck.owner_id].name} "
                f"({deckstats_deck.owner_id})..."
            )
            if str(deckstats_deck.saved_id) in imported_deckstats_deck:
                logger.debug(
                    f"Deck {deckstats_deck.saved_id} already stored on "
                    f"Storage (and Archive). Skipping it."
                )
                continue
            logger.info(f"Storing deck {deckstats_deck.saved_id} in Archive...")
            raw_deck = deckstats.get_deck(deckstats_deck.saved_id, use_cache=False)
            # sleep to avoid HTTPError: 429 Client Error: Too Many Requests
            time.sleep(REQUEST_SLEEP_TIMEOUT)
            playable_deck = deckstats.to_playable_deck(raw_deck)
            if playable_deck.len_mainboard != 60:
                logger.warning(f"Main deck has {playable_deck.len_mainboard} cards.")
            if playable_deck.len_sideboard != 15:
                logger.warning(f"Sideboard has {playable_deck.len_sideboard} cards.")
            suspicious_list = (
                playable_deck.len_mainboard != 60 or playable_deck.len_sideboard != 15
            )
            description = (
                f"Source: {deckstats_deck.url}\n"
                f"Creation date: {pretty_str(deckstats_deck.added)}"
            )
            if deckstats_deck.description:
                description += f"\nDescription: {deckstats_deck.description}"
            set_entry = set_index[int(deckstats_deck.p12e_code)]
            deck_name = (
                f"{deckstats_deck.name}.{deckstats_deck.owner_name} "
                f"| {set_entry['name']} ({set_entry['scryfall_code']})"
            )
            new_deck_id = self.create_deck(deck_name, description, playable_deck)
            storage_key = storage.get_imported_deckstats_deck_key(
                deckstats_deck.saved_id,
                new_deck_id,
                deck_name,
            )
            logger.info(f"Archiving information on storage in file {storage_key}...")
            storage.create_file(f"{storage_key}", str(playable_deck))
            if send_notification:
                logger.info("Informing player on Discord...")
                await discord.send_user_message(
                    player.discord_id,
                    f"📌 Imported deck: {deck_name}.\n\n"
                    f"Source: {deckstats_deck.url}\n\n"
                    f"Destination: {self.get_uri(new_deck_id)}",
                )
            if suspicious_list:
                await discord.send_user_message(
                    warning_player.discord_id,
                    f"⚠️ Archived deck with suspicious size "
                    f"(main: {playable_deck.len_mainboard}, "
                    f"sideboard: {playable_deck.len_sideboard})!\n\n"
                    f"Imported deck: {deck_name}.\n\n"
                    f"Source: {deckstats_deck.url}\n\n"
                    f"Destination: {self.get_uri(new_deck_id)}",
                )
        logger.info(f"Updated Archive decks for {player.name}.")

    async def archive_player_videos_from_twitch(
        self,
        player,
        videos,
        storage,
        discord,
        warning_player=PAUPERFORMANCE,
        send_notification=True,
    ):
        logger.info(f"Updating Archive videos for {player.name}...")
        imported_twitch_videos = storage.list_imported_twitch_videos_ids()
        for video in videos:
            logger.debug(
                f"Processing video '{video.title}' "
                f"({video.video_id}) "
                f"from {video.user_login_name}, "
                f"published on {video.published_at}, "
                f"url: {video.url}..."
            )
            if video.viewable != "public":
                await discord.send_user_message(
                    warning_player.discord_id,
                    f"⚠️ Skipped {video.viewable} Twitch video. "
                    f"'{video.title}' "
                    f"({video.video_id}) "
                    f"from {video.user_login_name}, "
                    f"published on {video.published_at}, "
                    f"url: {video.url}...",
                )
                continue

            if video.video_id in imported_twitch_videos:
                logger.debug(
                    f"Video {video.video_id} already stored on "
                    f"Storage. Skipping it."
                )
                continue
            if not video.deck_name:
                logger.debug(
                    f"Unable to find deck name for video {video.url}. "
                    f"Skipping it..."
                )
                continue
            storage_key = storage.get_imported_twitch_video_key(
                video.video_id,
                video.user_display_name,
                video.language,
                video.published_at.split("T")[0],
                video.deck_name,
            )
            logger.info(f"Archiving information on storage in file {storage_key}...")
            storage.create_file(
                f"{storage_key}",
                json.dumps(vars(video), indent=4),
            )
            if send_notification:
                logger.info("Informing player on Discord...")
                await discord.send_user_message(
                    player.discord_id,
                    f"📌 Imported video: {video.title}.\n\n"
                    f"Source: {video.url}\n\n"
                    f"Deck: {video.deck_name}",
                )
        logger.info(f"Updated Archive videos for {player.name}.")

    async def archive_player_videos_from_youtube(
        self,
        player,
        videos,
        storage,
        discord,
        warning_player=PAUPERFORMANCE,
        send_notification=True,
    ):
        logger.info(f"Updating Archive videos for {player.name}...")
        imported_youtube_videos = storage.list_imported_youtube_videos_ids()
        for video in videos:
            logger.debug(
                f"Processing video '{video.title}' "
                f"({video.content_video_id}) "
                f"from {video.channel_title}, "
                f"published on {video.published_at}, "
                f"url: {video.url}..."
            )

            if video.content_video_id in imported_youtube_videos:
                logger.debug(
                    f"Video {video.content_video_id} already stored on "
                    f"Storage. Skipping it."
                )
                continue

            if video.privacy_status != "public":
                await discord.send_user_message(
                    warning_player.discord_id,
                    f"⚠️ Skipped {video.privacy_status} YouTube video. "
                    f"'{video.title}' "
                    f"({video.content_video_id}) "
                    f"from {video.channel_title}, "
                    f"published on {video.published_at}, "
                    f"url: {video.url}...",
                )
                continue

            if not video.deck_name:
                logger.debug(
                    f"Unable to find deck name for video {video.url}. "
                    f"Skipping it..."
                )
                continue
            storage_key = storage.get_imported_youtube_video_key(
                video.content_video_id,
                video.channel_title,
                video.language,
                video.published_at.split("T")[0],
                video.deck_name,
            )
            logger.info(f"Archiving information on storage in file {storage_key}...")
            storage.create_file(
                f"{storage_key}",
                json.dumps(vars(video), indent=4),
            )
            if send_notification:
                logger.info("Informing player on Discord...")
                await discord.send_user_message(
                    player.discord_id,
                    f"📌 Imported video: {video.title}.\n\n"
                    f"Source: {video.url}\n\n"
                    f"Deck: {video.deck_name}",
                )
        logger.info(f"Updated Archive videos for {player.name}.")

    async def import_player_deck_from_mtggoldfish(
        self,
        url,
        player: PhD,
        pauperformance,
        discord_message,
        p12e_name=None,
        send_notification=True,
    ):
        author = discord_message.author
        discord = pauperformance.discord
        storage = pauperformance.storage
        logger.info(
            f"Importing into archive decks from url {url} for player "
            f"{player.name}..."
        )
        imported_mtggoldfish_decks = storage.list_imported_mtggoldfish_deck_ids()
        original_deck_id = url.rsplit("/")[-1]

        if original_deck_id in imported_mtggoldfish_decks:
            logger.debug(
                f"Deck {original_deck_id} already stored on "
                f"Storage (and Archive). Skipping it."
            )
            await discord_message.remove_reaction(
                DISCORD_MYR_REACTION_SEEN, discord.user
            )
            await discord_message.add_reaction(DISCORD_MYR_REACTION_OK)
            return

        logger.debug(f"Deck id: {original_deck_id}")
        all_archetypes = pauperformance.get_archetypes()
        all_decks = pauperformance.list_archived_decks()
        event = None
        if not p12e_name:
            logger.debug(f"Extracting deck info from url {url}...")
            content = urlopen(url).read().decode("utf-8")
            title_line = None
            event_line = None
            date_line = None
            for line in content.split("\n"):
                if "<title>" in line:
                    title_line = line
                elif MTGGOLDFISH_EVENT_LINE_TEXT in line:
                    event_line = line
                elif MTGGOLDFISH_DECK_DATE_TEXT in line:
                    date_line = line
            if event_line:
                soup = BeautifulSoup(event_line, features="lxml")
                event = soup.get_text()
                logger.debug(f"Polished event line: {event}")
            if not title_line or not date_line:
                message = (
                    f"Unable to find title ({title_line}) or date "
                    f"({date_line}) for url <{url}>. Skipping it."
                )
                logger.warning(message)
                await discord.send_log_message(message)
                await discord_message.remove_reaction(
                    DISCORD_MYR_REACTION_SEEN, discord.user
                )
                await discord_message.add_reaction(DISCORD_MYR_REACTION_KO)
                return
            soup = BeautifulSoup(title_line, features="lxml")
            title_line = soup.get_text()[: -len(" Deck")]
            logger.debug(f"Polished title line: {title_line}")
            p12e_name = title_line.split(" by ")[0]
            logger.debug(f"Extracted deck name: {p12e_name}")

            if not is_valid_p12e_deckstats_name(p12e_name):
                logger.debug(
                    f"Deck {p12e_name} has no legal p12e name. "
                    f"Trying to compute it..."
                )
                logger.debug("Computing set_id...")
                date = date_line.split(MTGGOLDFISH_DECK_DATE_TEXT)[1]
                logger.debug(f"Extracted deck date: {date}")
                dt = datetime.strptime(date, MTGGOLDFISH_DECK_PAGE_DATE_FORMAT)
                ms = datetime_to_ms(dt)
                logger.debug(f"{pretty_str(ms)}")
                usa_date = dt.strftime(USA_DATE_FORMAT)
                set_id = pauperformance.get_set_index_by_date(usa_date)
                logger.debug(f"Computed set_id: {set_id} (from date {usa_date}).")
                # assume p12e_name == archetype_name
                # search for all decks by player with same archetype and set_id
                deck_group = [
                    deck
                    for deck in all_decks
                    if deck.archetype == p12e_name
                    and int(deck.p12e_code) == set_id["p12e_code"]
                    and deck.owner_name == player.name
                ]
                logger.debug(
                    f"Found player decks with same archetype and set: " f"{deck_group}."
                )
                logger.debug("Computing revision...")
                if len(deck_group) == 0:
                    revision = "001"
                else:
                    revision = int(max((d.revision for d in deck_group)))
                    revision += 1
                    revision = str(revision).zfill(3)
                logger.debug(f"Computed revision: {revision}.")
                p12e_name = (
                    f"{p12e_name} " f"{set_id['p12e_code']}.{revision}.{player.name}"
                )
            else:
                p12e_name = f"{p12e_name}.{player.name}"
        logger.debug(f"Performing integrity checks on deck {p12e_name}...")
        creation_date = now_utc()
        tentative_deck = MTGGoldfishArchivedDeck(
            f"{p12e_name} | Foo (bar)",
            creation_date,
            original_deck_id,
        )

        if tentative_deck.archetype not in all_archetypes:
            message = (
                f"{DISCORD_MYR_REACTION_KO} Archetype "
                f"{tentative_deck.archetype} for "
                f"deck <{url}> is not among those valid ("
                f"<https://pauperformance.com/pages/archetypes_index.html>).\n"
                f"You can either delete the message from #import-deck or "
                f"rename the archetype to a valid one.\n"
                f"Please note archetypes have to be manually created by "
                f"admins. "
                f"If you think an archetype is missing, please let us know!\n"
                f"I will try to reimport the deck later."
            )
            logger.warning(message)
            if send_notification:
                await author.send(message)
            await discord.send_log_message(message)
            await discord_message.remove_reaction(
                DISCORD_MYR_REACTION_SEEN, discord.user
            )
            await discord_message.add_reaction(DISCORD_MYR_REACTION_KO)
            return

        deck_group = [d for d in all_decks if d.p12e_name == p12e_name]
        if len(deck_group) != 0:
            message = (
                f"Deck {p12e_name} already exists. "
                f"There are high chances you forgot to increase the "
                f"revision number. "
                f"Skipping deck <{url}>."
            )
            logger.warning(message)
            if send_notification:
                await author.send(message)
            await discord.send_log_message(message)
            await discord_message.remove_reaction(
                DISCORD_MYR_REACTION_SEEN, discord.user
            )
            await discord_message.add_reaction(DISCORD_MYR_REACTION_KO)
            return

        logger.debug(
            f"Processing deck '{p12e_name}' "
            f"({original_deck_id}) "
            f"from {player.name}..."
        )
        logger.info(f"Storing deck {original_deck_id} in Archive...")
        content = urlopen(tentative_deck.download_txt_url).read()
        lines = content.decode("utf-8").split("\r\n")
        playable_deck = parse_playable_deck_from_lines(lines)
        if playable_deck.len_mainboard != 60:
            logger.warning(f"Main deck has {playable_deck.len_mainboard} cards.")
        if playable_deck.len_sideboard != 15:
            logger.warning(f"Sideboard has {playable_deck.len_sideboard} cards.")
        suspicious_list = (
            playable_deck.len_mainboard != 60 or playable_deck.len_sideboard != 15
        )
        description = f"Source: {url}\n" f"Creation date: {pretty_str(creation_date)}"
        if event:
            description += f"\n{event}"
        set_index = pauperformance.set_index
        set_entry = set_index[int(tentative_deck.p12e_code)]
        deck_name = (
            f"{p12e_name} " f"| {set_entry['name']} ({set_entry['scryfall_code']})"
        )
        new_deck_id = self.create_deck(deck_name, description, playable_deck)
        storage_key = storage.get_imported_mtggoldfish_deck_key(
            original_deck_id,
            new_deck_id,
            deck_name,
        )
        logger.info(f"Archiving information on storage in file {storage_key}...")
        storage.create_file(f"{storage_key}", str(playable_deck))
        message = (
            f"📌 Imported deck: {deck_name}.\n\n"
            f"Source: <{url}>\n\n"
            f"Destination: <{self.get_uri(new_deck_id)}>"
        )
        if send_notification:
            logger.info("Informing player on Discord...")
            await author.send(message)
        await discord.send_log_message(message)
        await discord_message.remove_reaction(DISCORD_MYR_REACTION_SEEN, discord.user)
        # if the deck name was initially wrong but was later renamed and fixed,
        # there may be a DISCORD_MYR_REACTION_KO to remove
        await discord_message.remove_reaction(DISCORD_MYR_REACTION_KO, discord.user)
        await discord_message.add_reaction(DISCORD_MYR_REACTION_OK)
        if suspicious_list:
            message = (
                f"⚠️ Archived deck with suspicious size "
                f"(main: {playable_deck.len_mainboard}, "
                f"sideboard: {playable_deck.len_sideboard})!\n\n"
                f"Imported deck: {deck_name}.\n\n"
                f"Source: <{url}>\n\n"
                f"Destination: <{self.get_uri(new_deck_id)}>"
            )
            await author.send(message)
            await discord.send_log_message(message)
            await discord_message.add_reaction(DISCORD_MYR_REACTION_WARNING)
        logger.info(
            f"Imported into archive decks from url {url} for " f"player {player.name}."
        )
