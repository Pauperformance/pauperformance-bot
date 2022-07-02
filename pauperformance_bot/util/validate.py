from abc import ABCMeta
from copy import copy, deepcopy
from curses import meta
from functools import reduce
from typing import Any, Dict, List, Tuple, Union

from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard


class AbstractValidator(meta - ABCMeta):
    """Represents an instance of a validator for an object."""

    def validate(self) -> Tuple[bool, Any, Dict[str, List[str]]]:
        pass


class AbstractValueValidator(meta=ABCMeta):
    """Represents an instance of a validator for an immutable object."""

    def __init__(self) -> None:
        self._validated = False
        self._is_valid = False
        self._errors = {}

    def validate(self) -> Tuple[bool, Dict[str, List[str]]]:
        if self._validated:
            return self._is_valid, self._errors
        res = self._do_validation()
        self._validated = True
        return res

    def _do_validation(self) -> Tuple[bool, Dict[str, List[str]]]:
        pass


class BoardsValidator(AbstractValueValidator):
    def __init__(self, boards: Tuple[List[PlayedCard], List[PlayedCard]]) -> None:
        super().__init__()
        self._errors = {"mainboard": [], "sideboard": [], "whole": []}
        if not isinstance(boards, Tuple):
            self._errors["whole"].append("Input is not a Tuple")
            self._is_valid = False
            self._validated = True
        elif (
            len(boards) != 2
            or not isinstance(boards[0], list)
            or not isinstance(boards[1], list)
        ):
            self._errors["whole"].append("Input should contain exactly 2 List[str]")
            self._is_valid = False
            self._validated = True
        else:
            self._boards = boards

    def _do_validation(self) -> Tuple[bool, Dict[str, List[str]]]:
        return super()._do_validation()


class PlayableDeckValidator(AbstractValueValidator):
    def __init__(
        self,
        playable_deck: Union[PlayableDeck, Tuple[List[PlayedCard], List[PlayedCard]]],
    ) -> None:
        super().__init__()
        self._errors = {"mainboard": [], "sideboard": [], "whole": []}

        if isinstance(playable_deck, PlayableDeck) or (
            isinstance(playable_deck, Tuple)
            and len(playable_deck) == 2
            and isinstance(playable_deck[0], list)
            and isinstance(playable_deck[1], list)
        ):
            # self._deck =
            pass

    def validate(self) -> Tuple[bool, Dict[str, List[str]]]:
        """Checks that a PlayableDeck is a valid pauper deck.
        June 19, 2022. As described in the mtg website
        https://magic.wizards.com/en/formats/pauper
        a deck is a valid pauper deck if:
        - it has a minimum of 60 cards in the main deck (There is no maximum
          size for main decks)
        - it has up to 15 cards in your sideboard, if used
        - No more than four of any individual card in the main deck and
          sideboard combined (with the exception of basic lands)

        At this moment we cannot check the last rule, so that is being ignored.

        Returns:
            Tuple[bool, Dict[str, List[str]]]: a tuple where the first entry is true if
            and only if the boards are valid. The second entry is a dict containing
            the error messages for: mainboard, sideboard and whole, or an empty list if
            the boards are valid.
        """

        mainboard = []
        sideboard = []

        if isinstance(self._deck, Tuple):
            mainboard = self._deck[0]
            sideboard = self._deck[1]
        elif not isinstance(self._deck, PlayableDeck):
            is_valid = False
            self._errors["whole"].append(
                f"{type(self._deck)} is not an instance of {type(PlayableDeck)}"
            )
            return is_valid, self._errors
        else:
            mainboard = self._deck.mainboard
            sideboard = self._deck.sideboard

        main_amt = reduce(lambda t, s: t + s.quantity, mainboard, 0)
        if main_amt < PlayableDeck.MAINBOARD_MIN_AMOUNT:
            self._errors["mainboard"].append(
                f"Mainboard contains {main_amt} cards which is less than {PlayableDeck.MAINBOARD_MIN_AMOUNT}"
            )
            is_valid = False

        side_amt = reduce(lambda t, s: t + s.quantity, sideboard, 0)
        if side_amt > PlayableDeck.SIDEBOARD_MAX_AMOUNT:
            self._errors["mainboard"].append(
                f"Mainboard contains {side_amt} cards which is more than {PlayableDeck.SIDEBOARD_MAX_AMOUNT}"
            )
            is_valid = False

        return is_valid, self._errors

    def _check_copies(self, mainboard, sideboard) -> List[str]:
        # TODO fix this when we can check if a card is a land or not
        allcards = {}
        for pc in mainboard + sideboard:
            if pc.card_name not in allcards:
                allcards[pc.card_name] = 0
            allcards[pc.card_name] += pc.quantity

        return [
            f"{k} has more than {PlayableDeck.MAX_NON_LAND_QUANTITY} copies"
            for k in allcards.keys()
            if allcards[k] > PlayableDeck.MAX_NON_LAND_QUANTITY
        ]
