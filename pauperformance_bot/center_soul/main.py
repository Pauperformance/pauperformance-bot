import os
import re
from copy import copy
from os import path
from statistics import stdev, mean, variance
from typing import List, Optional, Dict, Tuple

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.pauperformance.archive.local import LocalArchiveService
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
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
        logger.error(f"Cannot parse {playable_deck_txt}. Error: {e}")
    finally:
        return playable_deck


class AcademyAssetsService:
    def __init__(self, academy_fs=AcademyFileSystem()):
        if not isinstance(academy_fs, AcademyFileSystem):
            raise ValueError(f"{type(academy_fs)} is not AcademyFileSystem")
        self._academy_fs = academy_fs

    def get_playable_decks(self, archetype) -> List[PlayableDeck]:
        deck_dir = posix_path(self._academy_fs.ASSETS_DATA_INTEL_DECK_DIR, archetype)
        if not path.exists(deck_dir):
            logger.error(
                f"No dir for archetype {archetype} found in "
                + f"{self._academy_fs.ASSETS_DATA_INTEL_DECK_DIR}"
            )
            return []
        playable_decks, missing = self.__load_all(deck_dir)
        if missing:
            logger.warning(
                f"{len(missing)} decks not found in "
                + f"{self._academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR} "
                + f"for archetype {archetype}: {missing}"
            )
        return playable_decks

    def __load_all(self, deck_dir):
        missing = []
        playable_decks = []
        for deck_file in os.listdir(deck_dir):
            with open(posix_path(deck_dir, deck_file)) as deck_f:
                deck: Deck = jsonpickle.decode(deck_f.read(), safe=True)
                deck_id = re.sub(r"^.*/", "", deck.url)
            playable_deck_txt = posix_path(
                self._academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                f"{deck_id}.txt",
            )
            if not path.exists(playable_deck_txt):
                missing.append(deck_id)
                continue
            playable = load_deck(playable_deck_txt)
            if playable:
                playable_decks.append(playable)
        return playable_decks, missing


class ArchetypeMeta:
    def __init__(
        self,
        name: str,
        playable_decks: List[PlayableDeck],
        cards: Dict[str, Dict[str, int]],
    ):
        self.name = name
        self._playable_decks = playable_decks
        self._cards = cards

    @property
    def nr_decks(self) -> int:
        return len(self._playable_decks)

    @property
    def cards(self) -> List[str]:
        return list(self._cards.keys())

    @property
    def most_played(self) -> str:
        return max(self._cards.items(), key=lambda x: x[1]["count"])

    @property
    def total_played(self) -> int:
        return sum(card["count"] for _, card in self._cards.items())

    @property
    def deck_frequencies(self) -> List[Tuple[str, float]]:
        return sorted(
            list(
                map(
                    lambda card: (card[0], card[1]["decks"] / self.nr_decks),
                    self._cards.items(),
                )
            ),
            key=lambda x: x[1],
            reverse=True,
        )

    @property
    def card_frequencies(self) -> List[Tuple[str, float]]:
        total = self.total_played
        return sorted(
            list(
                map(
                    lambda card: (card[0], card[1]["count"] / total),
                    self._cards.items(),
                )
            ),
            key=lambda x: x[1],
            reverse=True,
        )


class ArchetypeMetaFactory:
    def __init__(self, academy: AcademyService, assets_service: AcademyAssetsService):
        if not isinstance(academy, AcademyService):
            raise ValueError(f"{type(academy)} is not an AcademyService")
        if not isinstance(assets_service, AcademyAssetsService):
            raise ValueError(f"{type(assets_service)} is not an AcademyAssetsService")
        self._academy = academy
        self._assets_service = assets_service

    def build_meta_for(self, archetype: str) -> ArchetypeMeta:
        playable_decks = self._assets_service.get_playable_decks(archetype)
        logger.debug(f"Found {len(playable_decks)} decks for {archetype}")
        cards = {}
        for i, pd in enumerate(playable_decks):
            for card in pd.sideboard + pd.mainboard:
                sf_card = self._academy.scryfall.get_card_named(
                    card.card_name, fuzzy=True
                )
                if not sf_card:
                    logger.warning(
                        f"Cannot fetch {card.card_name} from Scryfall card will still be included in centroid"
                    )
                elif "land" in sf_card["type_line"].lower():
                    logger.debug(f"Skipping land {card.card_name}")
                    continue
                if card.card_name not in cards:
                    cards[card.card_name] = {"decks": 0, "count": 0}
                cards[card.card_name]["decks"] += 1
                cards[card.card_name]["count"] += card.quantity
        return ArchetypeMeta(archetype, playable_decks, cards)


class ArchetypeCentroid:
    def __init__(self, meta: ArchetypeMeta):
        if not meta or not isinstance(meta, ArchetypeMeta):
            raise ValueError(f"{type(meta)} is not ArchetypeMeta")
        self._cards = sorted(list(filter(lambda f: f[1] >= 0.9, meta.deck_frequencies)))

    @property
    def cards(self) -> List[Tuple[str, float]]:
        return copy(self._cards)

    def __repr__(self):
        return f"Nr. Cards: {len(self._cards)} Cards: {self._cards}"

    def __str__(self):
        return f"{self._cards}"


def test_outputs(am: ArchetypeMeta):
    logger.info(am.cards)
    logger.info(f"nr. decks: {am.nr_decks} max: {am.most_played}")
    dfq = am.deck_frequencies
    cfq = am.card_frequencies
    logger.info("# DECKS")
    logger.info(f"max deck freq.: {dfq[0]}")
    logger.info(
        f"staples(decks): {sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.9, dfq))))}"
    )
    deck_freqs = [f[1] for f in dfq]
    mean_deck_freq = mean(deck_freqs)
    logger.info(
        f"stdev: {stdev(deck_freqs)} mean {mean_deck_freq} variance: {variance(deck_freqs)}"
    )
    logger.info(
        f"staples(decks): {sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= mean_deck_freq + stdev(deck_freqs), dfq))))}"
    )
    logger.info("# CARDS")
    logger.info(f"max card freq {cfq[0]}")
    logger.info(
        f"staples(cards): {sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.07, cfq))))}"
    )
    card_freqs = [f[1] for f in cfq]
    mean_card_freq = mean(card_freqs)
    logger.info(
        f"stdev: {stdev(card_freqs)} mean {mean_card_freq} variance: {variance(card_freqs)}"
    )
    s_card_fqs = sorted(
        list(
            map(
                lambda f: f[0],
                filter(lambda f: f[1] >= mean_card_freq + stdev(card_freqs), cfq),
            )
        )
    )
    logger.info(f"staples(cards): {s_card_fqs}")


def main():
    storage = LocalStorageService()
    archive = LocalArchiveService()
    pauperformance = PauperformanceService(storage, archive)
    academy = AcademyService(pauperformance)
    archetype = "Izzet Faeries"
    # index = academy.set_index
    # logger.info(index)
    aas = AcademyAssetsService()
    am = ArchetypeMetaFactory(academy, aas).build_meta_for(archetype)
    centroid = ArchetypeCentroid(am)
    logger.info(centroid.__repr__())


if __name__ == "__main__":
    # TODO remove me!
    main()
