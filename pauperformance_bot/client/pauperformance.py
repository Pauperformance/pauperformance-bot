import glob
from functools import lru_cache
from pathlib import Path
from time import sleep

from pauperformance_bot.client.deckstats import Deckstats
from pauperformance_bot.client.scryfall import Scryfall
from pauperformance_bot.constants import \
    SET_INDEX_TEMPLATE_FILE, SET_INDEX_OUTPUT_FILE, TEMPLATES_PAGES_DIR, \
    CONFIG_ARCHETYPES_DIR, TEMPLATES_ARCHETYPES_DIR, \
    PAUPERFORMANCE_ARCHETYPES_DIR, ARCHETYPE_TEMPLATE_FILE, \
    KNOWN_SET_WITH_NO_PAUPER_CARDS, PAUPER_POOL_TEMPLATE_FILE, \
    PAUPER_POOL_OUTPUT_FILE
from pauperformance_bot.players import PAUPERFORMANCE_PLAYERS
from pauperformance_bot.util.config import read_config, read_archetype_config
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.template import render_template
from pauperformance_bot.util.time import pretty_str, now

logger = get_application_logger()


class Pauperformance:
    def __init__(self, scryfall=Scryfall(), players=PAUPERFORMANCE_PLAYERS):
        self.scryfall = scryfall
        self.players = players

    @lru_cache(maxsize=1)
    def get_set_index(self):
        logger.info("Building set index...")
        sets = self.scryfall.get_sets()
        sorted_sets = sorted(
            sets['data'], key=lambda s: s['released_at'] + s['code']
        )
        logger.info("Built set index.")
        return [
            {
                "p12e_code": p12e_code,
                "scryfall_code": s['code'],
                "name": s['name'],
                "date": s['released_at'],
            } for p12e_code, s in enumerate(sorted_sets, start=1)
        ]

    def update_set_index(
            self,
            templates_pages_dir=TEMPLATES_PAGES_DIR,
            set_index_template_file=SET_INDEX_TEMPLATE_FILE,
            set_index_output_file=SET_INDEX_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering set index in {templates_pages_dir} from {set_index_template_file}..."
        )
        render_template(
            templates_pages_dir,
            set_index_template_file,
            set_index_output_file,
            {
                "index": self.get_set_index(),
                "last_update_date": pretty_str(now()),
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
            values['staples'] = self._get_rendered_card_info(values['staples'])
            values['frequents'] = self._get_rendered_card_info(values['frequents'])
            archetype_name = values['name']
            values['decks'] = [
                deck
                for deck in all_decks
                if deck.archetype == archetype_name
            ]
            archetype_file_name = Path(archetype_config_file).name

            archetype_output_file = posix_path(
                pauperformance_archetypes_dir,
                archetype_file_name.replace('.ini', '.md'),
            )
            logger.info(
                f"Rendering {archetype_name} in {templates_archetypes_dir} from {archetype_template_file}..."
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
            f"Rendering pauper pool in {templates_pages_dir} from {pauper_pool_template_file}..."
        )
        set_index = self.get_set_index()
        card_index = self.get_pauper_cards_incremental_index()
        render_template(
            templates_pages_dir,
            pauper_pool_template_file,
            pauper_pool_output_file,
            {
                "tot_cards_number": sum(len(i) for i in card_index.values()),
                "set_index": set_index,
                "card_index": card_index,
                "last_update_date": pretty_str(now()),
            }
        )
        logger.info(f"Rendered pauper pool to {pauper_pool_template_file}.")

    def _get_rendered_card_info(self, cards):
        rendered_cards = []
        for card in sorted(cards):
            scryfall_card = self.scryfall.get_card_named(card)
            rendered_cards.append({
                'name': card,
                "image_url": scryfall_card["image_uris"]["normal"],
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
        return sorted(all_decks, reverse=True, key=lambda d: d.p13e_code)

    @lru_cache(maxsize=1)
    def get_pauper_cards_index(self, skip_sets=KNOWN_SET_WITH_NO_PAUPER_CARDS):
        set_index = self.get_set_index()
        card_index = {}
        count = 0
        for item in set_index:
            p12e_code = item['p12e_code']
            # if p12e_code != 677:
            #     continue
            if p12e_code in skip_sets:
                card_index[p12e_code] = []
                continue
            scryfall_code = item['scryfall_code']
            query = f"set:{scryfall_code} rarity:common legal:pauper"
            cards = self.scryfall.search_cards(query)
            card_index[p12e_code] = cards
            count += 1
            if count == 2:
                break
            sleep(0.3)
        return card_index

    @lru_cache(maxsize=1)
    def get_pauper_cards_incremental_index(self):
        card_index = self.get_pauper_cards_index()
        incremental_card_index = {}
        existing_card_names = set()
        for p12e_code, cards in card_index.items():
            logger.info(f"Processing set with p12e_code: {p12e_code}...")
            new_cards = []
            for card in cards:
                if card['name'] in existing_card_names:
                    continue
                new_cards.append(card)
                existing_card_names.add(card['name'])
            incremental_card_index[p12e_code] = new_cards
            logger.info(f"Found {len(new_cards)} new cards.")
            logger.info(f"Processed set with p12e_code: {p12e_code}.")
        return incremental_card_index
