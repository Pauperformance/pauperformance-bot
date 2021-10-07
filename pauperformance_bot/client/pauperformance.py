import glob
import pickle
from collections import OrderedDict
from pathlib import Path
from time import sleep

from pauperformance_bot.client.deckstats import Deckstats
from pauperformance_bot.client.scryfall import Scryfall
from pauperformance_bot.constants import \
    CONFIG_ARCHETYPES_DIR, KNOWN_SETS_WITH_NO_PAUPER_CARDS, \
    PAUPER_CARDS_INDEX_CACHE_FILE, LAST_SET_INDEX_FILE
from pauperformance_bot.players import PAUPERFORMANCE_PLAYERS
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class Pauperformance:
    def __init__(self, scryfall=Scryfall(), players=PAUPERFORMANCE_PLAYERS):
        self.scryfall = scryfall
        self.players = players
        self.set_index = OrderedDict()

        self._build_set_index()

    def _build_set_index(self, last_set_index_file=LAST_SET_INDEX_FILE):
        logger.info("Building Scryfall set index...")
        scryfall_sets = self.scryfall.get_sets()
        scryfall_sets = sorted(
            scryfall_sets['data'], key=lambda s: s['released_at'] + s['code']
        )
        logger.info("Built Scryfall set index.")

        logger.info("Building Pauperformance set index...")
        with open(last_set_index_file, "rb") as index_f:
            self.set_index = pickle.load(index_f)
        known_sets = {s['scryfall_code'] for s in self.set_index.values()}
        p12e_code = max(self.set_index.keys()) + 1
        for s in scryfall_sets:
            if s['code'] in known_sets:
                continue
            self.set_index[p12e_code] = {
                "p12e_code": p12e_code,
                "scryfall_code": s['code'],
                "name": s['name'],
                "date": s['released_at'],
            }
            p12e_code += 1
        logger.info("Built Pauperformance set index.")

        logger.info("Saving Pauperformance set index...")
        with open(last_set_index_file, 'wb') as index_f:
            pickle.dump(self.set_index, index_f)
        logger.info("Saved Pauperformance set index.")

    def get_pauper_cards_index(
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
            logger.warn(
                f"Please, update the list of known sets with no pauper cards adding: {sorted(list(to_be_removed_sets))}"
            )

        with open(cards_index_cache_file, 'wb') as cache_f:
            pickle.dump(card_index, cache_f)
        return card_index

    def get_pauper_cards_incremental_index(self):
        incremental_card_index = {}
        existing_card_names = set()
        for p12e_code, cards in self.get_pauper_cards_index().items():
            logger.debug(f"Processing set with p12e_code: {p12e_code}...")

            if 'Promos' in self.set_index[p12e_code]['name'] or \
                    'Black Border' in self.set_index[p12e_code]['name']:
                logger.debug(f"Skipping set {self.set_index[p12e_code]['name']}...")
                incremental_card_index[p12e_code] = []
                continue

            new_cards = []
            for card in cards:
                if card['name'] in existing_card_names:
                    continue
                new_cards.append(card)
                existing_card_names.add(card['name'])
            incremental_card_index[p12e_code] = new_cards
            logger.debug(f"Found {len(new_cards)} new cards.")
            logger.debug(f"Processed set with p12e_code: {p12e_code}.")
        return incremental_card_index

    def get_pauperformance_decks(self):
        all_decks = []
        for player in self.players:
            logger.info(f"Processing player {player.name}...")
            deckstats = Deckstats(owner_id=player.deckstats_id)
            player_decks = deckstats.list_pauperformance_decks(player.deckstats_name)
            logger.info(f"Found {len(player_decks)} decks.")
            all_decks += player_decks
        all_decks.sort(reverse=True, key=lambda d: d.p12e_code)
        archetypes = get_pauperformance_archetypes()
        for deck in all_decks:
            if deck.archetype not in archetypes:
                logger.warn(
                    f"Deck {deck.name} by {deck.owner_name} doesn't match any "
                    f"known archetype."
                )
        return all_decks

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


def get_pauperformance_archetypes(config_pages_dir=CONFIG_ARCHETYPES_DIR):
    return set(
        Path(a).name.replace(".ini", "")
        for a in glob.glob(f"{config_pages_dir}/*.ini")
    )
