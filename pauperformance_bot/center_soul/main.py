import os
import re
from os import path
from typing import List, Optional, Dict

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.deck.playable import PlayableDeck, parse_playable_deck_from_lines
from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.pauperformance.archive.local import LocalArchiveService
from pauperformance_bot.service.pauperformance.pauperformance import PauperformanceService
from pauperformance_bot.service.pauperformance.storage.local import LocalStorageService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


def load_deck(playable_deck_txt) -> Optional[PlayableDeck]:
    playable_deck = None
    try:
        with open(playable_deck_txt) as playable_f:
            lines = [line.strip() for line in playable_f.readlines()]
            playable_deck = parse_playable_deck_from_lines(lines)
    except Exception as e:
        logger.error(f'Cannot parse {playable_deck_txt}. Error: {e}')
    finally:
        return playable_deck


class AcademyAssetsService:

    def __init__(self, academy_fs=AcademyFileSystem()):
        if not isinstance(academy_fs, AcademyFileSystem):
            raise ValueError(f'{type(academy_fs)} is not AcademyFileSystem')
        self._academy_fs = academy_fs

    def get_playable_decks(self, archetype) -> List[PlayableDeck]:
        deck_dir = posix_path(self._academy_fs.ASSETS_DATA_INTEL_DECK_DIR, archetype)
        if not path.exists(deck_dir):
            logger.error(f'No dir for archetype {archetype} found in ' +
                         f'{self._academy_fs.ASSETS_DATA_INTEL_DECK_DIR}')
            return []
        playable_decks, missing = self.__load_all(deck_dir)
        if missing:
            logger.warning(f'{len(missing)} decks not found in ' +
                           f'{self._academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR} ' +
                           f'for archetype {archetype}: {missing}')
        return playable_decks
    
    def __load_all(self, deck_dir):
        missing = []
        playable_decks = []
        for deck_file in os.listdir(deck_dir):
            with open(posix_path(deck_dir, deck_file)) as deck_f:
                deck: Deck = jsonpickle.decode(deck_f.read(), safe=True)
                deck_id = re.sub(r'^.*/', '', deck.url)
            playable_deck_txt = posix_path(self._academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                                           f'{deck_id}.txt')
            if not path.exists(playable_deck_txt):
                missing.append(deck_id)
                continue
            playable = load_deck(playable_deck_txt)
            if playable:
                playable_decks.append(playable)
        return playable_decks, missing


class ArchetypeMeta:

    def __init__(self, name: str, playable_decks: List[PlayableDeck],
                 cards: Dict[str, Dict[str, int]]):
        self.name = name
        self._playable_decks = playable_decks
        self._cards = cards

    @property
    def nr_decks(self):
        return len(self._playable_decks)

    @property
    def cards(self):
        return self._cards.keys()

    @property
    def most_played(self):
        return max(self._cards.items(), key=lambda x: x[1]["count"])

class ArchetypeMetaFactory:

    def __init__(self, academy: AcademyService, assets_service: AcademyAssetsService):
        if not isinstance(academy, AcademyService):
            raise ValueError(f'{type(academy)} is not an AcademyService')
        if not isinstance(assets_service, AcademyAssetsService):
            raise ValueError(f'{type(assets_service)} is not an AcademyAssetsService')
        self._academy = academy
        self._assets_service = assets_service

    def build_meta_for(self, archetype: str) -> ArchetypeMeta:
        playable_decks = self._assets_service.get_playable_decks(archetype)
        logger.debug(f'Found {len(playable_decks)} decks for {archetype}')
        cards = {}
        for i, pd in enumerate(playable_decks):
            for card in pd.sideboard + pd.mainboard:
                sf_card = self._academy.scryfall.get_card_named(card.card_name)
                if not sf_card:
                    logger.error(f'Cannot fetch {card.card_name} from Scryfall '
                                 + 'card will still be included in centroid')
                elif 'land' in sf_card['type_line'].lower():
                    logger.debug(f'Skipping land {card.card_name}')
                    continue
                if card.card_name not in cards:
                    cards[card.card_name] = {'decks': 0, 'count': 0}
                cards[card.card_name]['decks'] += 1
                cards[card.card_name]['count'] += card.quantity
        return ArchetypeMeta(archetype, playable_decks, cards)


def main():
    storage = LocalStorageService()
    archive = LocalArchiveService()
    pauperformance = PauperformanceService(storage, archive)
    academy = AcademyService(pauperformance)
    archetype = 'Burn'
    # index = academy.set_index
    # logger.info(index)
    aas = AcademyAssetsService()
    am = ArchetypeMetaFactory(academy, aas).build_meta_for(archetype)
    logger.info(am.cards)

    logger.info(f'nr. decks: {am.nr_decks} max: {am.most_played}')


if __name__ == '__main__':
    # TODO remove me!
    main()

