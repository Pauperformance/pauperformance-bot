from pauperformance_bot.entity.played_cards import PlayedCard


class PlayableDeck:
    def __init__(
        self,
        mainboard: list[PlayedCard],
        sideboard: list[PlayedCard],
    ):
        self.mainboard: list[PlayedCard] = mainboard
        self.sideboard: list[PlayedCard] = sideboard

    @property
    def mainboard_mtggoldfish(self):
        return "\n".join((f"{c.quantity} {c.card_name}" for c in self.mainboard))

    @property
    def sideboard_mtggoldfish(self):
        return "\n".join((f"{c.quantity} {c.card_name}" for c in self.sideboard))

    @property
    def mainboard_cards_map(self):
        return {
            played_card.card_name: played_card.quantity
            for played_card in self.mainboard
        }

    @property
    def sideboard_cards_map(self):
        return {
            played_card.card_name: played_card.quantity
            for played_card in self.sideboard
        }

    @property
    def len_mainboard(self):
        return sum(c.quantity for c in self.mainboard)

    @property
    def len_sideboard(self):
        return sum(c.quantity for c in self.sideboard)

    def is_legal(self, banned_cards_names):
        banned_cards_names = set(banned_cards_names)
        if len({c.card_name for c in self.mainboard} & banned_cards_names) != 0:
            return False
        if len({c.card_name for c in self.sideboard} & banned_cards_names) != 0:
            return False
        return True

    def __str__(self):
        return (
            f"Main ({self.len_mainboard}):\n{self.mainboard_mtggoldfish}\n\n"
            f"Sideboard ({self.len_sideboard}):\n{self.sideboard_mtggoldfish}"
        )

    def __repr__(self):
        return (
            " ".join((repr(c) for c in self.mainboard))
            + "|"
            + " ".join((repr(c) for c in self.sideboard))
        )

    def __hash__(self):
        return hash(repr(self))


def parse_playable_deck_from_lines(lines) -> PlayableDeck:
    separator = lines.index("")
    maindeck = lines[:separator]
    maindeck.sort(key=lambda pc: pc.split(" ", maxsplit=1)[1])
    sideboard = lines[separator + 1 : -1]
    sideboard.sort(key=lambda pc: pc.split(" ", maxsplit=1)[1])
    return PlayableDeck(
        [PlayedCard(*(line.split(" ", maxsplit=1))) for line in maindeck],
        [PlayedCard(*(line.split(" ", maxsplit=1))) for line in sideboard],
    )


def _get_plus_minus_diff(deck1_cards_map, deck2_cards_map):
    minus_list, plus_list = [], []
    for card, qty in deck1_cards_map.items():
        if card not in deck2_cards_map:
            minus_list.append(f"{qty} {card}")
        if card in deck2_cards_map:
            qty2 = deck2_cards_map[card]
            if qty == qty2:
                continue
            elif qty > qty2:
                minus_list.append(f"{qty - qty2} {card}")
            else:
                plus_list.append(f"{qty2 - qty} {card}")
    for card, qty in deck2_cards_map.items():
        if card not in deck1_cards_map:
            plus_list.append(f"{qty} {card}")
    return minus_list, plus_list


def get_decks_diff(deck1, deck2):
    main_minus_list, main_plus_list = _get_plus_minus_diff(
        deck1.mainboard_cards_map,
        deck2.mainboard_cards_map,
    )
    side_minus_list, side_plus_list = _get_plus_minus_diff(
        deck1.sideboard_cards_map,
        deck2.sideboard_cards_map,
    )
    return main_minus_list, main_plus_list, side_minus_list, side_plus_list


def print_decks_diff(deck1, deck2):
    (
        main_minus_list,
        main_plus_list,
        side_minus_list,
        side_plus_list,
    ) = get_decks_diff(deck1, deck2)
    print("MAIN:")
    for minus in main_minus_list:
        print(f"-{minus}")
    for plus in main_plus_list:
        print(f"+{plus}")
    print("\nSIDEBOARD:")
    for minus in side_minus_list:
        print(f"-{minus}")
    for plus in side_plus_list:
        print(f"+{plus}")
