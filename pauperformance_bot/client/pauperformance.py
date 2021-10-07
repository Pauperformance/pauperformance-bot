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
    PAUPER_POOL_PAGE_NAME, SET_INDEX_PATCH, LAST_SET_INDEX_FILE
from pauperformance_bot.players import PAUPERFORMANCE_PLAYERS
from pauperformance_bot.util.config import read_config, read_archetype_config
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.template import render_template
from pauperformance_bot.util.time import pretty_str, now

logger = get_application_logger()


class Pauperformance:
    pass
