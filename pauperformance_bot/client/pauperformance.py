import glob
from pathlib import Path

from pauperformance_bot.client.deckstats import Deckstats
from pauperformance_bot.client.scryfall import Scryfall
from pauperformance_bot.constants import \
    SET_INDEX_TEMPLATE_FILE, SET_INDEX_OUTPUT_FILE, TEMPLATES_PAGES_DIR, \
    CONFIG_ARCHETYPES_DIR, TEMPLATES_ARCHETYPES_DIR, \
    PAUPERFORMANCE_ARCHETYPES_DIR, ARCHETYPE_TEMPLATE_FILE
from pauperformance_bot.players import PAUPERFORMANCE_PLAYERS
from pauperformance_bot.util.config import read_config, read_archetype_config
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.template import render_template
from pauperformance_bot.util.time import pretty_str, now

logger = get_application_logger()


class Pauperformance:
    def __init__(self, scryfall=Scryfall()):
        self.scryfall = scryfall

    def get_set_index(self):
        logger.info("Building set index...")
        sets = self.scryfall.get_sets()
        sorted_sets = sorted(
            sets['data'], key=lambda s: s['released_at'] + s['code']
        )
        logger.info("Built set index.")
        return [
            {
                "index": index,
                "code": s['code'],
                "name": s['name'],
                "date": s['released_at'],
            } for index, s in enumerate(sorted_sets, start=1)
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
                deck for deck in all_decks if deck.archetype == archetype_name
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

    def get_pauperformance_decks(self):
        all_decks = []
        for player in PAUPERFORMANCE_PLAYERS:
            logger.info(f"Processing player {player.name}...")
            deckstats = Deckstats(owner_id=player.deckstats_id)
            player_decks = deckstats.list_pauperformance_decks(player.deckstats_name)
            logger.info(f"Found {len(player_decks)} decks.")
            all_decks += player_decks
        return all_decks
