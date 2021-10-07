import glob
import pickle
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from time import sleep

from pauperformance_bot.client.deckstats import Deckstats
from pauperformance_bot.client.scryfall import Scryfall
from pauperformance_bot.constants import \
    SET_INDEX_TEMPLATE_FILE, SET_INDEX_OUTPUT_FILE, TEMPLATES_PAGES_DIR, \
    CONFIG_ARCHETYPES_DIR, TEMPLATES_ARCHETYPES_DIR, \
    PAUPERFORMANCE_ARCHETYPES_DIR, ARCHETYPE_TEMPLATE_FILE, \
    KNOWN_SETS_WITH_NO_PAUPER_CARDS, PAUPER_POOL_TEMPLATE_FILE, \
    PAUPER_POOL_OUTPUT_FILE, SET_INDEX_PAGE_NAME, \
    PAUPER_CARDS_INDEX_CACHE_FILE, ARCHETYPES_INDEX_TEMPLATE_FILE, \
    ARCHETYPES_INDEX_OUTPUT_FILE, PAUPERFORMANCE_ARCHETYPES_DIR_RELATIVE_URL, \
    PAUPER_POOL_PAGE_NAME, LAST_SET_INDEX_FILE
from pauperformance_bot.players import PAUPERFORMANCE_PLAYERS
from pauperformance_bot.util.config import read_archetype_config
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.template import render_template
from pauperformance_bot.util.time import pretty_str, now

logger = get_application_logger()


class Academy:
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

    def update_all(self):
        self.update_archetypes_index()
        self.update_set_index()
        self.update_pauper_pool()
        self.update_archetypes()

    def update_archetypes_index(
            self,
            config_pages_dir=CONFIG_ARCHETYPES_DIR,
            templates_pages_dir=TEMPLATES_PAGES_DIR,
            archetypes_dir=PAUPERFORMANCE_ARCHETYPES_DIR_RELATIVE_URL,
            archetypes_index_template_file=ARCHETYPES_INDEX_TEMPLATE_FILE,
            archetypes_index_output_file=ARCHETYPES_INDEX_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering archetype index in {templates_pages_dir} from "
            f"{archetypes_index_template_file}..."
        )
        archetypes = []
        for archetype_config_file in glob.glob(f"{config_pages_dir}/*.ini"):
            logger.info(f"Processing {archetype_config_file}")
            values = read_archetype_config(archetype_config_file)
            archetypes.append({
                "name": values["name"],
                "mana": values["mana"],
                "type": ', '.join(values["type"]),
            })
        archetypes.sort(key=lambda a: a['name'])
        render_template(
            templates_pages_dir,
            archetypes_index_template_file,
            archetypes_index_output_file,
            {
                "archetypes": archetypes,
                "last_update_date": pretty_str(now()),
                "archetypes_dir": archetypes_dir,
            }
        )
        logger.info(
            f"Rendered archetypes index to {archetypes_index_output_file}."
        )

    def update_set_index(
            self,
            templates_pages_dir=TEMPLATES_PAGES_DIR,
            set_index_template_file=SET_INDEX_TEMPLATE_FILE,
            set_index_output_file=SET_INDEX_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering set index in {templates_pages_dir} from {set_index_template_file}..."
        )
        bolded_set_index = self._boldify_sets_with_new_cards()
        render_template(
            templates_pages_dir,
            set_index_template_file,
            set_index_output_file,
            {
                "index": bolded_set_index,
                "last_update_date": pretty_str(now()),
                "pauper_pool_page": PAUPER_POOL_PAGE_NAME.as_html(),
            }
        )
        logger.info(f"Rendered set index to {set_index_output_file}.")

    def update_archetypes(
            self,
            config_pages_dir=CONFIG_ARCHETYPES_DIR,
            templates_archetypes_dir=TEMPLATES_ARCHETYPES_DIR,
            archetype_template_file=ARCHETYPE_TEMPLATE_FILE,
            pauperformance_archetypes_dir=PAUPERFORMANCE_ARCHETYPES_DIR,
    ):
        logger.info(f"Generating archetypes...")
        all_decks = self.get_pauperformance_decks()
        for archetype_config_file in glob.glob(f"{config_pages_dir}/*.ini"):
            logger.info(f"Processing {archetype_config_file}")
            values = read_archetype_config(archetype_config_file)
            archetype_name = values['name']
            archetype_decks = [
                deck
                for deck in all_decks
                if deck.archetype == archetype_name
            ]
            staples, frequents = self._analyze_cards_frequency(archetype_decks)
            if len(archetype_decks) < 2:
                logger.warn(
                    f"{archetype_name} doesn't have at least 2 decks to generate staples and frequent cards."
                )
            values['staples'] = self._get_rendered_card_info(staples)
            values['frequents'] = self._get_rendered_card_info(frequents)
            values['decks'] = archetype_decks
            archetype_file_name = Path(archetype_config_file).name
            if archetype_name != archetype_file_name.replace(".ini", ""):
                logger.warn(
                    f"Archetype config mismatch: {archetype_name} vs "
                    f"{archetype_file_name}"
                )

            archetype_output_file = posix_path(
                pauperformance_archetypes_dir,
                archetype_file_name.replace('.ini', '.md'),
            )
            logger.info(
                f"Rendering {archetype_name} in {templates_archetypes_dir} "
                f"from {archetype_template_file}..."
            )
            render_template(
                templates_archetypes_dir,
                archetype_template_file,
                archetype_output_file,
                values,
            )
        logger.info(f"Generated archetypes.")

    def update_pauper_pool(
            self,
            templates_pages_dir=TEMPLATES_PAGES_DIR,
            pauper_pool_template_file=PAUPER_POOL_TEMPLATE_FILE,
            pauper_pool_output_file=PAUPER_POOL_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering pauper pool in {templates_pages_dir} from "
            f"{pauper_pool_template_file}..."
        )
        card_index = self.get_pauper_cards_incremental_index()
        render_template(
            templates_pages_dir,
            pauper_pool_template_file,
            pauper_pool_output_file,
            {
                "tot_cards_number": sum(len(i) for i in card_index.values()),
                "set_index": list(self.set_index.values()),
                "card_index": card_index,
                "last_update_date": pretty_str(now()),
                "set_index_page": SET_INDEX_PAGE_NAME.as_html(),
            }
        )
        logger.info(f"Rendered pauper pool to {pauper_pool_template_file}.")

    def _get_rendered_card_info(self, cards):
        rendered_cards = []
        for card in sorted(cards):
            scryfall_card = self.scryfall.get_card_named(card)
            if "image_uris" not in scryfall_card:  # e.g. Delver of Secrets
                image_uris = scryfall_card["card_faces"][0]["image_uris"]
            else:
                image_uris = scryfall_card["image_uris"]
            rendered_cards.append({
                'name': card,
                "image_url": image_uris["normal"],
                "page_url": scryfall_card["scryfall_uri"].replace('?utm_source=api', ''),
            })
        return rendered_cards

    @lru_cache(maxsize=1)
    def get_pauperformance_decks(self):
        all_decks = []
        for player in self.players:
            logger.info(f"Processing player {player.name}...")
            deckstats = Deckstats(owner_id=player.deckstats_id)
            player_decks = deckstats.list_pauperformance_decks(player.deckstats_name)
            logger.info(f"Found {len(player_decks)} decks.")
            all_decks += player_decks
        all_decks.sort(reverse=True, key=lambda d: d.p13e_code)
        archetypes = self.get_pauperformance_archetypes()
        for deck in all_decks:
            if deck.archetype not in archetypes:
                logger.warn(
                    f"Deck {deck.name} by {deck.owner_name} doesn't match any "
                    f"known archetype."
                )
        return all_decks

    def get_pauperformance_archetypes(
            self,
            config_pages_dir=CONFIG_ARCHETYPES_DIR
    ):
        return set(
            Path(a).name.replace(".ini", "")
            for a in glob.glob(f"{config_pages_dir}/*.ini")
        )

    @lru_cache(maxsize=1)
    def get_pauper_cards_index(
            self,
            skip_sets=KNOWN_SETS_WITH_NO_PAUPER_CARDS,
            cards_index_cache_file=PAUPER_CARDS_INDEX_CACHE_FILE,
    ):
        card_index = {}
        try:
            with open(cards_index_cache_file, "rb") as cache_f:
                card_index = pickle.load(cache_f)
                logger.debug(f"Loaded card index from cache: {card_index}")
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
        logger.info(
            f"Feel free to update the list of known sets with no pauper cards: "
            f"{[i for i in card_index if len(card_index[i]) == 0]}"
        )
        with open(cards_index_cache_file, 'wb') as cache_f:
            pickle.dump(card_index, cache_f)
        return card_index

    def get_pauper_cards_incremental_index(self):
        card_index = self.get_pauper_cards_index()
        incremental_card_index = {}
        existing_card_names = set()
        for p12e_code, cards in card_index.items():
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

    def _boldify_sets_with_new_cards(self):
        card_index = self.get_pauper_cards_incremental_index()
        bolded_index = []
        for item in self.set_index.values():
            p12e_code = item['p12e_code']
            if len(card_index[p12e_code]) == 0:
                bolded_index.append(item)
            else:
                bolded_index.append({
                    k: f"**{v}**"
                    for k, v in item.items()
                })
        return bolded_index

    def _analyze_cards_frequency(self, archetype_decks):
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
