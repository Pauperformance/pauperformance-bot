from pauperformance_bot.client.scryfall import Scryfall
from pauperformance_bot.constants import TEMPLATES_DIR, \
    SET_INDEX_TEMPLATE_FILE, SET_INDEX_OUTPUT_FILE
from pauperformance_bot.util.log import get_application_logger
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

    def render_set_index(
            self,
            templates_dir=TEMPLATES_DIR,
            set_index_template_file=SET_INDEX_TEMPLATE_FILE,
            set_index_output_file=SET_INDEX_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering set index in {templates_dir} from {set_index_template_file}..."
        )
        render_template(
            templates_dir,
            set_index_template_file,
            set_index_output_file,
            {
                "index": self.get_set_index(),
                "last_update_date": pretty_str(now()),
            }
        )
        logger.info(f"Rendered set index to {set_index_output_file}.")
