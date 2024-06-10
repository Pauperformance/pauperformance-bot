import os
import re
from copy import copy
from os import path
from statistics import mean, stdev, variance
from typing import Dict, List, Optional, Tuple

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
    """Service to load in memory all the known intel regarding decks."""

    def __init__(self, academy_fs=AcademyFileSystem()):
        if not isinstance(academy_fs, AcademyFileSystem):
            raise ValueError(f"{type(academy_fs)} is not AcademyFileSystem")
        self._academy_fs = academy_fs

    def get_playable_decks(self, archetype) -> List[PlayableDeck]:
        """Returns a list of decks for the given archetype."""
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
    """Represents metadata related to an archetype."""

    def __init__(
        self,
        name: str,
        playable_decks: List[PlayableDeck],
        cards: Dict[str, Dict[str, int]],
    ):
        self.name = name
        self._playable_decks = playable_decks
        self._cards = cards
        self.most_played_card = None

        total = 0
        most_played = 0
        for card in cards.items():
            total += card[1]["total_quantity"]

            if card[1]["total_quantity"] > most_played:
                most_played = card[1]["total_quantity"]
                self.most_played_card = card[0]

        self.played_cards_total = total

    def nr_decks(self) -> int:
        """Returns the total amount of known decks for the archetype."""
        return len(self._playable_decks)

    def cards(self) -> List[str]:
        """Returns the list of all card names which have been played
        (either main or side) for the archetype."""
        return list(self._cards.keys())

    def deck_occurrences_ratio(self) -> List[Tuple[str, float]]:
        """Returns a list of all the cards ever played for this archetype
        and their ratio of decks containing the card over the total count of decks."""
        return sorted(
            list(
                map(
                    lambda card: (card[0], card[1]["nr_decks"] / self.nr_decks()),
                    self._cards.items(),
                )
            ),
            key=lambda x: x[1],
            reverse=True,
        )

    def card_playing_rate(self) -> List[Tuple[str, float]]:
        """Returns a list of all cards ever played for this archetype
        and the corresponding ratio of total quantity and the total nr. of cards
        in all decks."""
        return sorted(
            list(
                map(
                    lambda card: (
                        card[0],
                        card[1]["total_quantity"] / self.played_cards_total,
                    ),
                    self._cards.items(),
                )
            ),
            key=lambda x: x[1],
            reverse=True,
        )

    def cards_breakdown(self) -> Dict[str, List[int]]:
        """Returns a list of all cards ever played for this archetype
        and the relative list of rate of observations of decks in which this card is
        played in either 1, 2, 3, or 4 copies."""
        return dict(
            map(
                lambda card: (
                    card[0],
                    list(
                        map(lambda x: x / self.nr_decks(), card[1]["quantity_buckets"])
                    ),
                ),
                self._cards.items(),
            )
        )


class ArchetypeMetaFactory:
    def __init__(self, academy: AcademyService, assets_service: AcademyAssetsService):
        if not isinstance(academy, AcademyService):
            raise ValueError(f"{type(academy)} is not an AcademyService")
        if not isinstance(assets_service, AcademyAssetsService):
            raise ValueError(f"{type(assets_service)} is not an AcademyAssetsService")
        self._academy = academy
        self._assets_service = assets_service

    # TODO add expansion set filter
    def build_meta_for(self, archetype: str) -> ArchetypeMeta:
        playable_decks = self._assets_service.get_playable_decks(archetype)
        logger.debug(f"Found {len(playable_decks)} decks for {archetype}")
        all_cards = {}

        for pd in playable_decks:
            occurred_in_deck = set()
            # build a lookup dict for card stats
            for card in pd.mainboard + pd.sideboard:
                sf_card = self._academy.scryfall.get_card_named(
                    card.card_name, fuzzy=False
                )
                if not sf_card:
                    logger.error(f"Card not found in scryfall {card.card_name}")
                    continue

                if card.card_name not in all_cards:
                    all_cards[card.card_name] = {
                        "nr_decks": 0,
                        "total_quantity": 0,
                        # count decks having 1, 2, 3, 4 copies
                        "quantity_buckets": [0, 0, 0, 0],
                    }

                if card.card_name not in occurred_in_deck:
                    all_cards[card.card_name]["nr_decks"] += 1
                    occurred_in_deck.add(card.card_name)

                for i in range(1, 5):
                    if i == card.quantity:
                        all_cards[card.card_name]["quantity_buckets"][i - 1] += 1

                all_cards[card.card_name]["total_quantity"] += card.quantity

        return ArchetypeMeta(archetype, playable_decks, all_cards)


class ArchetypeCentroid:
    """Value class to represent staple cards of an archetype."""

    def __init__(self, meta: ArchetypeMeta):
        if not meta or not isinstance(meta, ArchetypeMeta):
            raise ValueError(f"{type(meta)} is not ArchetypeMeta")
        self._cards = sorted(
            list(filter(lambda f: f[1] >= 0.9, meta.deck_occurrences_ratio()))
        )

    @property
    def cards(self) -> List[Tuple[str, float]]:
        return copy(self._cards)

    def __repr__(self):
        return f"Nr. Cards: {len(self._cards)} Cards: {self._cards}"

    def __str__(self):
        return f"{self._cards}"


def manual_test_outputs(am: ArchetypeMeta):
    logger.info(am.cards)
    logger.info(f"nr. decks: {am.nr_decks} max: {am.most_played}")
    dfq = am.deck_occurrences_ratio()
    cfq = am.card_playing_rate()
    logger.info("# DECKS")
    logger.info(f"max deck freq.: {dfq[0]}")
    centroid = sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.9, dfq))))
    logger.info(f"centroid(decks): {centroid}")
    deck_freqs = [f[1] for f in dfq]
    mean_deck_freq = mean(deck_freqs)
    logger.info(f"stdev: {stdev(deck_freqs)}  variance: {variance(deck_freqs)}")
    logger.info(f"mean {mean_deck_freq}")
    logger.info("# CARDS")
    logger.info(f"max card freq {cfq[0]}")
    centroid = sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.07, cfq))))
    logger.info(f"centroid(cards): {centroid}")
    card_freqs = [f[1] for f in cfq]
    mean_card_freq = mean(card_freqs)
    logger.info(f"stdev: {stdev(card_freqs)} variance: {variance(card_freqs)}")
    logger.info(f"mean {mean_card_freq}")
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
    archetype = "Burn"
    # index = academy.set_index
    # logger.info(index)
    aas = AcademyAssetsService()
    am = ArchetypeMetaFactory(academy, aas).build_meta_for(archetype)
    centroid = ArchetypeCentroid(am)
    logger.info(centroid.__repr__())
    logger.info("Cards breakdown: ")
    logger.info(am.cards_breakdown())


if __name__ == "__main__":
    # TODO remove main
    main()
