import glob
import pickle
from datetime import datetime
from pathlib import Path
from time import sleep

from pauperformance_bot.client.deckstats import Deckstats
from pauperformance_bot.client.dropbox_ import Dropbox
from pauperformance_bot.client.mtggoldfish import MTGGoldfish
from pauperformance_bot.client.myr import Myr
from pauperformance_bot.client.scryfall import Scryfall
from pauperformance_bot.constant.dropbox import DECKSTATS_DECKS_PATH
from pauperformance_bot.constant.mtggoldfish import DECK_API_ENDPOINT
from pauperformance_bot.constant.myr import LAST_SET_INDEX_FILE, PAUPER_CARDS_INDEX_CACHE_FILE, CONFIG_ARCHETYPES_DIR
from pauperformance_bot.constant.pauperformance import KNOWN_SETS_WITH_NO_PAUPER_CARDS, \
    INCREMENTAL_CARDS_INDEX_SKIP_SETS
from pauperformance_bot.constant.players import PAUPERFORMANCE_PLAYERS, PAUPERFORMANCE_PLAYER, SHIKA93_PLAYER
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import pretty_str

logger = get_application_logger()


class Pauperformance:
    def __init__(
            self,
            scryfall=Scryfall(),
            mtggoldfish=MTGGoldfish(),
            dropbox=Dropbox(),
            myr=Myr(),
            players=PAUPERFORMANCE_PLAYERS,
    ):
        self.scryfall = scryfall
        self.mtggoldfish = mtggoldfish
        self.dropbox = dropbox
        self.myr = myr
        self.players = players
        self.set_index = self._build_set_index()
        self.card_index = self._build_card_index()
        self.incremental_card_index = self._build_incremental_card_index()

    def _build_set_index(self, last_set_index_file=LAST_SET_INDEX_FILE):
        logger.info("Building Scryfall set index...")
        scryfall_sets = self.scryfall.get_sets()
        scryfall_sets = sorted(
            scryfall_sets['data'], key=lambda s: s['released_at'] + s['code']
        )
        logger.info("Built Scryfall set index.")

        logger.info("Building Pauperformance set index...")
        with open(last_set_index_file, "rb") as index_f:
            set_index = pickle.load(index_f)
        known_sets = {s['scryfall_code'] for s in set_index.values()}
        p12e_code = max(set_index.keys()) + 1
        for s in scryfall_sets:
            if s['code'] in known_sets:
                continue
            set_index[p12e_code] = {
                "p12e_code": p12e_code,
                "scryfall_code": s['code'],
                "name": s['name'],
                "date": s['released_at'],
            }
            p12e_code += 1
        logger.info("Built Pauperformance set index.")

        logger.info("Saving Pauperformance set index...")
        with open(last_set_index_file, 'wb') as index_f:
            pickle.dump(set_index, index_f)
        logger.info("Saved Pauperformance set index.")
        return set_index

    def _build_card_index(
            self,
            skip_sets=KNOWN_SETS_WITH_NO_PAUPER_CARDS,
            cards_index_cache_file=PAUPER_CARDS_INDEX_CACHE_FILE,
    ):
        card_index = {}
        try:
            with open(cards_index_cache_file, "rb") as cache_f:
                card_index = pickle.load(cache_f)
                logger.debug(f"Loaded card index from cache: {cards_index_cache_file}")
        except FileNotFoundError:
            logger.debug("No cache found for card index.")

        for item in self.set_index.values():
            p12e_code = item['p12e_code']
            if p12e_code in card_index:
                continue  # cached
            if p12e_code in skip_sets:
                card_index[p12e_code] = []
                continue
            scryfall_code = item['scryfall_code']
            query = f"set:{scryfall_code} rarity:common legal:pauper"
            cards = self.scryfall.search_cards(query)
            card_index[p12e_code] = cards
            sleep(0.3)
        useless_sets = set(i for i in card_index if len(card_index[i]) == 0)
        to_be_removed_sets = useless_sets - set(KNOWN_SETS_WITH_NO_PAUPER_CARDS)
        if len(to_be_removed_sets) > 0:
            logger.warning(
                f"Please, update the list of known sets with no pauper cards adding: {sorted(list(to_be_removed_sets))}"
            )

        with open(cards_index_cache_file, 'wb') as cache_f:
            pickle.dump(card_index, cache_f)
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

            if p12e_code in skip_sets or \
                    'Promos' in self.set_index[p12e_code]['name'] or \
                    'Black Border' in self.set_index[p12e_code]['name']:
                logger.debug(f"Skipping set {self.set_index[p12e_code]['name']}...")
                incremental_card_index[p12e_code] = []
                useless_sets.add(p12e_code)
                continue

            new_cards = []
            for card in cards:
                if card['name'] in existing_card_names:
                    continue
                new_cards.append(card)
                existing_card_names.add(card['name'])
            incremental_card_index[p12e_code] = new_cards
            logger.debug(f"Found {len(new_cards)} new cards.")
        to_be_removed_sets = useless_sets - set(INCREMENTAL_CARDS_INDEX_SKIP_SETS)
        if len(to_be_removed_sets) > 0:
            logger.warning(
                f"Please, update the list of known sets to be skipped for the incremental cards index adding: {sorted(list(to_be_removed_sets))}"
            )
        return incremental_card_index

    def get_deckstats_decks(self):
        all_decks = []
        for player in self.players:
            logger.info(f"Processing player {player.name}...")
            deckstats = Deckstats(owner_id=player.deckstats_id)
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

    def get_mtggoldfish_decks(self):
        return self.mtggoldfish.list_decks()

    def get_archetypes(self, config_pages_dir=CONFIG_ARCHETYPES_DIR):
        return set(
            Path(a).name.replace(".ini", "")
            for a in glob.glob(f"{config_pages_dir}/*.ini")
        )

    def analyze_cards_frequency(self, archetype_decks):
        if len(archetype_decks) < 2:
            return [], []
        lands = set(land['name'] for land in self.scryfall.get_legal_lands())
        deckstats_accounts = {}
        decks_cards = {}
        all_cards = set()
        for deck in archetype_decks:
            owner_id = str(deck.owner_id)
            deckstats = deckstats_accounts.get(
                owner_id, Deckstats(owner_id=owner_id)
            )
            deckstats_accounts[owner_id] = deckstats
            deck_content = deckstats.get_deck(str(deck.saved_id))
            if len(deck_content['sections']) != 1:
                logger.error(f"More than one section for deck {deck.saved_id}")
                raise ValueError()
            cards = [c['name'] for c in deck_content['sections'][0]['cards']]
            decks_cards[deck.saved_id] = cards
            all_cards.update(cards)
        staples = set(all_cards)
        for deck_list in decks_cards.values():
            staples = staples & set(deck_list)
        staples = staples - lands
        frequents = all_cards - staples - lands
        return list(staples), list(frequents)

    def import_mtggoldfish_decks(self):
        logger.info("Updating MTGGoldfish decks for all users...")
        for player in self.players:
            self.import_mtggoldfish_player_decks(player)
        logger.info("Updated MTGGoldfish decks for all users.")

    def import_mtggoldfish_player_decks(
            self,
            player,
            dropbox_deckstats_path=DECKSTATS_DECKS_PATH,
    ):
        logger.info(f"Updating MTGGoldfish decks for {player.name}...")
        deckstats = Deckstats(owner_id=player.deckstats_id)
        imported_deckstats_deck = set(
            file_metadata.path_display.rsplit('/', maxsplit=1)[1].split('>')[0]
            for file_metadata in self.dropbox.list_files(dropbox_deckstats_path)
        )
        players_by_deckstats_id = {int(p.deckstats_id): p for p in self.players}
        for deckstats_deck in deckstats.list_pauperformance_decks(player.deckstats_name):
            logger.debug(
                f"Processing deck '{deckstats_deck.name}' ({deckstats_deck.saved_id}) "
                f"from {deckstats_deck.owner_name}, "
                f"uploaded by {players_by_deckstats_id[deckstats_deck.owner_id].name} ({deckstats_deck.owner_id})..."
            )
            if str(deckstats_deck.saved_id) in imported_deckstats_deck:
                logger.debug(
                    f"Deck {deckstats_deck.saved_id} already stored on Dropbox (and MTGGoldfish). Skipping it."
                )
                continue
            logger.info(f"Storing deck {deckstats_deck.saved_id} on MTGGoldfish...")
            raw_deck = deckstats.get_deck(deckstats_deck.saved_id, use_cache=False)
            playable_deck = deckstats.to_playable_deck(raw_deck)
            if playable_deck.len_mainboard != 60:
                logger.warning(f"Main deck has {playable_deck.len_mainboard} cards.")
            if playable_deck.len_sideboard != 15:
                logger.warning(f"Sideboard has {playable_deck.len_sideboard} cards.")
            suspicious_list = playable_deck.len_mainboard != 60 or playable_deck.len_sideboard != 15
            description = f"Source: {deckstats_deck.url}\n" \
                          f"Creation date: {pretty_str(deckstats_deck.added)}"
            if deckstats_deck.description:
                description += f"\nDescription: {deckstats_deck.description}"
            set_entry = self.set_index[int(deckstats_deck.p12e_code)]
            deck_name = f"{deckstats_deck.name}.{deckstats_deck.owner_name} " \
                        f"| {set_entry['name']} ({set_entry['scryfall_code']})"
            mtggoldfish_deck_id = self.mtggoldfish.create_deck(deck_name, description, playable_deck)
            dropbox_key = f"{dropbox_deckstats_path}/{deckstats_deck.saved_id}>{mtggoldfish_deck_id}>{deck_name}.txt"
            logger.info(f"Archiving information in Dropbox in file {dropbox_key}...")
            self.dropbox.create_file(f"{dropbox_key}", str(playable_deck))
            logger.info(f"Informing player on Telegram...")
            self.myr.send_message(
                player,
                f"📌 Imported deck: {deck_name}.\n\n"
                f"Source: {deckstats_deck.url}\n\n"
                f"Destination: {DECK_API_ENDPOINT}/{mtggoldfish_deck_id}",
            )
            if suspicious_list:
                self.myr.send_message(
                    PAUPERFORMANCE_PLAYER,
                    f"⚠️ Archived deck with suspicious size "
                    f"(main: {playable_deck.len_mainboard}, sideboard: {playable_deck.len_sideboard})!\n\n"
                    f"Imported deck: {deck_name}.\n\n"
                    f"Source: {deckstats_deck.url}\n\n"
                    f"Destination: {DECK_API_ENDPOINT}/{mtggoldfish_deck_id}",
                )
        logger.info(f"Updated MTGGoldfish decks for {player.name}.")

    def get_set_index_by_date(self, usa_date):
        logger.debug(f"Getting set index for USA date {usa_date}")
        return [
            s for s in self.set_index.values()
            if s['date'] <= usa_date and len(self.incremental_card_index.get(s['p12e_code'])) > 0
        ][-1]

    def get_current_set_index(self):
        return self.get_set_index_by_date(datetime.today().strftime('%Y-%m-%d'))


if __name__ == '__main__':
    p12e = Pauperformance()
    p12e.import_mtggoldfish_player_decks(SHIKA93_PLAYER)
    # p12e.get_current_set_index()
    # p12e.import_mtggoldfish_decks()
