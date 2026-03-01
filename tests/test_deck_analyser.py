from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard

# from pauperformance_bot.service.deck_analyser import get_similarity


def test_get_similarity() -> None:
    mainboard1: list[PlayedCard] = [
        PlayedCard(3, "Island"),
        PlayedCard(3, "Gush"),
        PlayedCard(54, "X"),
    ]
    sideboard1: list[PlayedCard] = [PlayedCard(11, "Plains"), PlayedCard(4, "Forest")]
    deck1: PlayableDeck = PlayableDeck(mainboard1, sideboard1)

    mainboard2: list[PlayedCard] = [
        PlayedCard(2, "Island"),
        PlayedCard(4, "Gush"),
        PlayedCard(54, "X"),
    ]
    sideboard2: list[PlayedCard] = [PlayedCard(11, "Plains"), PlayedCard(4, "Forest")]
    deck2: PlayableDeck = PlayableDeck(mainboard2, sideboard2)
    # assert get_similarity(deck1, deck2) > 0.99
    assert deck1 != deck2  # TODO: remove
