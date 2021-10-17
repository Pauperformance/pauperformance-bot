import time
from abc import ABCMeta, abstractmethod

from pauperformance_bot.constant.deckstats import REQUEST_SLEEP_TIMEOUT
from pauperformance_bot.constant.players import PAUPERFORMANCE_PLAYER
from pauperformance_bot.service.mtg.deckstats import DeckstatsService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import pretty_str

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
    def to_playable_deck(listed_deck, decks_cache_dir, use_cache=True):
        pass

    def import_player_decks_from_deckstats(
        self,
        player,
        storage,
        players_by_deckstats_id,
        set_index,
        myr,
        warning_player=PAUPERFORMANCE_PLAYER,
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
            logger.info(
                f"Storing deck {deckstats_deck.saved_id} in Archive..."
            )
            raw_deck = deckstats.get_deck(
                deckstats_deck.saved_id, use_cache=False
            )
            # sleep to avoid HTTPError: 429 Client Error: Too Many Requests
            time.sleep(REQUEST_SLEEP_TIMEOUT)
            playable_deck = deckstats.to_playable_deck(raw_deck)
            if playable_deck.len_mainboard != 60:
                logger.warning(
                    f"Main deck has {playable_deck.len_mainboard} cards."
                )
            if playable_deck.len_sideboard != 15:
                logger.warning(
                    f"Sideboard has {playable_deck.len_sideboard} cards."
                )
            suspicious_list = (
                playable_deck.len_mainboard != 60
                or playable_deck.len_sideboard != 15
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
            new_deck_id = self.create_deck(
                deck_name, description, playable_deck
            )
            storage_key = storage.get_imported_deckstats_deck_key(
                deckstats_deck.saved_id,
                new_deck_id,
                deck_name,
            )
            logger.info(
                f"Archiving information on storage in file {storage_key}..."
            )
            storage.create_file(f"{storage_key}", str(playable_deck))
            if send_notification:
                logger.info("Informing player on Telegram...")
                myr.send_message(
                    player,
                    f"📌 Imported deck: {deck_name}.\n\n"
                    f"Source: {deckstats_deck.url}\n\n"
                    f"Destination: {self.get_uri(new_deck_id)}",
                )
            if suspicious_list:
                myr.send_message(
                    warning_player,
                    f"⚠️ Archived deck with suspicious size "
                    f"(main: {playable_deck.len_mainboard}, "
                    f"sideboard: {playable_deck.len_sideboard})!\n\n"
                    f"Imported deck: {deck_name}.\n\n"
                    f"Source: {deckstats_deck.url}\n\n"
                    f"Destination: {self.get_uri(new_deck_id)}",
                )
        logger.info(f"Updated Archive decks for {player.name}.")
