from pauperformance_bot.constant.players import SHIKA93_PLAYER
from pauperformance_bot.entity.deck.playable import (
    parse_playable_deck_from_lines,
    print_decks_diff,
)
from pauperformance_bot.service.mtg.deckstats import DeckstatsService


def _get_playable_decks(deck1_uri, deck2_uri):
    deckstats = DeckstatsService(SHIKA93_PLAYER.deckstats_id)
    deck1_id = deck1_uri.split("/")[-1].split("-")[0]
    deck1 = deckstats.get_deck(deck1_id)
    deck1 = deckstats.to_playable_deck(deck1)
    with open(deck2_uri, "r") as in_f:
        lines = [line[:-1] for line in in_f.readlines()] + [""]
        del lines[lines.index("")]
        deck2 = parse_playable_deck_from_lines(lines)
    return deck1, deck2


def diff_deck_v2(deck1_uri, deck2_uri):
    deck1, deck2 = _get_playable_decks(deck1_uri, deck2_uri)
    print_decks_diff(deck1, deck2)


def main():
    deck1 = (
        "https://deckstats.net/decks/78813/1483869-devo-stompy-beta1-2019-bb-"
    )
    deck1 = "https://deckstats.net/decks/78813/1312551-ur-skred-rc2-mengucci-2019-bb-"
    deck1 = "https://deckstats.net/decks/78813/1312586-orzhov-pestilence-rc2-2019-bb-"
    deck1 = "https://deckstats.net/decks/78813/1111479-boros-monarch-rc2-thraben27-20"
    deck1 = "https://deckstats.net/decks/78813/1312553-burn-rc2-supercow12653-2019-bb"
    deck1 = "https://deckstats.net/decks/78813/1312938-bogles-rc2-themaverickgirl-201"
    deck1 = "https://deckstats.net/decks/78813/1304623-elves-rc2-themaverickgal-2019-"
    deck1 = "https://deckstats.net/decks/78813/1312561-monow-heroic-rc1-dhalsinbh1-20"
    deck1 = (
        "https://deckstats.net/decks/78813/773091-bg-aristocrats-rc1-2018-bb-"
    )
    deck2 = "/home/gianvito/Downloads/Ixidor29 (3rd Place).txt"  # stompy 3
    deck2 = (
        "/home/gianvito/Downloads/Mogged (2nd Place).txt"  # izzet faeries 2
    )
    deck2 = (
        "/home/gianvito/Downloads/Kampo (1st Place).txt"  # orzhov pestilence 1
    )
    deck2 = (
        "/home/gianvito/Downloads/carvs (11th Place).txt"  # boros monarch 11
    )
    deck2 = "/home/gianvito/Downloads/PRGJJAR (24th Place).txt"  # burn 1
    deck2 = "/home/gianvito/Downloads/SanPop (1st Place).txt"  # bogles 1
    deck2 = "/home/gianvito/Downloads/tarmogoyf_ita (1st Place).txt"  # elves 1
    deck2 = "/home/gianvito/Downloads/Mono W Heroic.txt"  # heroic
    deck2 = "/home/gianvito/Downloads/Condescend (4th Place).txt"  # affo
    deck2 = "/home/gianvito/Downloads/Deck - Goblin Burn.txt"  # goblins
    deck2 = "/home/gianvito/Downloads/Deck - Mono-Black Control.txt"  # MBC
    deck2 = "/home/gianvito/Downloads/Aristocrats BG a Pauper deck by Gandalf_the_Magician.txt"  # Aristocrats
    # diff_deck(deck1, deck2)
    diff_deck_v2(deck1, deck2)


if __name__ == "__main__":
    main()
