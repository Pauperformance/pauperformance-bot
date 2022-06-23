import pytest

from pauperformance_bot.deckstructor.PoolWarning import PoolWarning
from pauperformance_bot.deckstructor.main import extract_deck
from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard


def test_deckstructor():
    expected_deck = PlayableDeck(mainboard=[
        PlayedCard(2, 'Boseiju, Who Endures'),
        PlayedCard(4, 'Cavern of Souls'),
        PlayedCard(2, 'Forest'),
        PlayedCard(2, 'Misty Rainforest'),
        PlayedCard(4, 'Nurturing Peatland'),
        PlayedCard(1, 'Nykthos, Shrine to Nyx'),
        PlayedCard(2, 'Overgrown Tomb'),
        PlayedCard(2, 'Verdant Catacombs'),
        PlayedCard(2, 'Yavimaya, Cradle of Growth'),
        PlayedCard(4, 'Collected Company'),
        PlayedCard(4, 'Dwynen\'s Elite'),
        PlayedCard(4, 'Elvish Archdruid'),
        PlayedCard(3, 'Elvish Champion'),
        PlayedCard(4, 'Elvish Mystic'),
        PlayedCard(4, 'Elvish Warmaster'),
        PlayedCard(1, 'Ezuri, Renegade Leader'),
        PlayedCard(4, 'Heritage Druid'),
        PlayedCard(4, 'Llanowar Elves'),
        PlayedCard(1, 'Quirion Ranger'),
        PlayedCard(4, 'Shaman of the Pack'),
        PlayedCard(2, 'Unearth')
    ],
        sideboard=[
            PlayedCard(4, 'Endurance'),
            PlayedCard(1, 'Ezuri, Renegade Leader'),
            PlayedCard(1, 'Force of Vigor'),
            PlayedCard(3, 'Reclamation Sage'),
            PlayedCard(2, 'Sylvan Anthem'),
            PlayedCard(1, 'Unearth'),
            PlayedCard(3, 'Veil of Summer')
        ]
    )

    with open('tests/mock_data/modern_mtg_elves.txt', 'r') as f:
        text = f.read()

    with open('tests/mock_data/pool.txt', 'r') as f:
        pool = f.readlines()

    pool = [p.strip() for p in pool]
    with pytest.warns(PoolWarning):
        deck = extract_deck(text, pool)
    assert deck == expected_deck
