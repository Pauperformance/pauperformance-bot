from scipy import spatial

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard

SIDEBOARD_W = 0.25


def _get_playable_decks():
    mainboard1 = [
        PlayedCard(3, "Island"),
        PlayedCard(3, "Gush"),
        PlayedCard(54, "C"),
    ]
    sideboard1 = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]

    mainboard2 = [
        PlayedCard(2, "Island"),
        PlayedCard(4, "Gush"),
        PlayedCard(54, "C"),
    ]
    sideboard2 = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]

    return (
        PlayableDeck(mainboard1, sideboard1),
        PlayableDeck(mainboard2, sideboard2),
    )


def sim_cos(v1, v2, w=1.0):
    if w == 0:
        return 1
    return 1 - spatial.distance.cosine(v1, v2, w=len(v1) * [w])


def vectorize(cards_map1, cards_map2):
    all_cards = list(set(cards_map1.keys()).union(set(cards_map2.keys())))
    all_cards.sort()
    return (
        [cards_map1.get(c, 0) for c in all_cards],
        [cards_map2.get(c, 0) for c in all_cards],
    )


def main():
    deck1, deck2 = _get_playable_decks()
    vector_main1, vector_main2 = vectorize(
        deck1.mainboard_cards_map,
        deck2.mainboard_cards_map,
    )
    vector_side1, vector_side2 = vectorize(
        deck1.sideboard_cards_map,
        deck2.sideboard_cards_map,
    )
    sim_main = sim_cos(vector_main1, vector_main2)
    sim_side = sim_cos(vector_side1, vector_side2, 0)
    sim = sim_main * sim_side
    print(f"sim_main: {sim_main}")
    print(f"sim_side: {sim_side}")
    print(f"sim: {sim}")


if __name__ == "__main__":
    main()
