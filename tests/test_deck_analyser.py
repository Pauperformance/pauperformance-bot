from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard

# from pauperformance_bot.service.deck_analyser import get_similarity


def test_get_similarity():
    mainboard1 = [
        PlayedCard(3, "Island"),
        PlayedCard(3, "Gush"),
        PlayedCard(54, "X"),
    ]
    sideboard1 = [PlayedCard(11, "Plains"), PlayedCard(4, "Forest")]
    deck1 = PlayableDeck(mainboard1, sideboard1)

    mainboard2 = [
        PlayedCard(2, "Island"),
        PlayedCard(4, "Gush"),
        PlayedCard(54, "X"),
    ]
    sideboard2 = [PlayedCard(11, "Plains"), PlayedCard(4, "Forest")]
    deck2 = PlayableDeck(mainboard2, sideboard2)
    # assert get_similarity(deck1, deck2) > 0.99
    assert deck1 != deck2  # TODO: remove
