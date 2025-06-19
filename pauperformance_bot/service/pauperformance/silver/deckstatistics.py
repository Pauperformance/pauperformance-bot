from typing import Dict, List, Tuple

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.exceptions import CardNotFoundException
from pauperformance_bot.service.academy.data_loader import AcademyDataLoader
from pauperformance_bot.service.mtg.scryfall import ScryfallService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class Deckstatistics:
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

    def get_cards_above_frequency(self, threshold: float):
        return sorted(
            list(filter(lambda f: f[1] >= threshold, self.deck_occurrences_ratio()))
        )

    def get_staple_and_frequent_cards(
        self, staple_threshold=0.9, frequent_threshold=0.7
    ):
        staple_cards = set(
            c[0] for c in self.get_cards_above_frequency(staple_threshold)
        )
        frequent_cards = set(
            c[0] for c in self.get_cards_above_frequency(frequent_threshold)
        )
        return sorted(list(staple_cards)), sorted(list(frequent_cards - staple_cards))


class DeckstatisticsFactory:
    def __init__(self, scryfall: ScryfallService, academy_loader: AcademyDataLoader):
        self._scryfall: ScryfallService = scryfall
        self._academy_loader = academy_loader

    # TODO add expansion set filter
    def build_metadata_for(self, archetype: str) -> Deckstatistics:
        playable_decks = self._academy_loader.load_classified_decks(archetype)
        logger.debug(f"Found {len(playable_decks)} decks for {archetype}")
        all_cards = {}

        for pd in playable_decks:
            occurred_in_deck = set()
            # build a lookup dict for card stats
            for card in pd.mainboard + pd.sideboard:
                try:
                    self._scryfall.get_card_named(card.card_name)
                except CardNotFoundException:
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

        return Deckstatistics(archetype, playable_decks, all_cards)
