# TODO: replace UB MTGO version names
# TODO: replace single cards with dual cards
# eg (Stormshriek Feral -> Stormshriek Feral // Flush Out)

TYPOS = {
    "SB: 1 ": "",
    "SB: 2 ": "",
    "SB: 3 ": "",
    "SB: 4 ": "",
    "\\'s": "'s",
    "Boros Garrinson": "Boros Garrison",
    "TerrariÃ³n": "Terrarion",
    "fanatic offering": "Fanatical Offering",
    "hunter's bowgun": "Hunter's Blowgun",
    "LÃÂ³rien Revealed": "Lórien Revealed",
    "Plain": "Plains",
    "Plainss": "Plains",
    "Eletrickery": "Electrickery",
    "Epic Confrotation": "Epic Confrontation",
    "fist of ironwood": "Fists of Ironwood",
    "Clockwork Percusionist": "Clockwork Percussionist",
    "Birechole Rangers": "Birchlore Rangers",
    "Viridian Longbo": "Viridian Longbow",
    "Viridian Longboww": "Viridian Longbow",
    "pulse of murassa": "Pulse of Murasa",
    "Snow-Covered plain": "Snow-Covered Plains",
    "Snow-Covered Plainss": "Snow-Covered Plains",
    "Ãvarax": "Avarax",
    "Muntain": "Mountain",
    "Village Rite": "Village Rites",
    "Village Ritess": "Village Rites",
    "Corrupted convinction": "Corrupted Conviction",
    "Anchovy &amp; Banana Pizza": "Anchovy & Banana Pizza",
    "Resistir a tempestade": "Weather the Storm",
    "lightining bolt": "Lightning Bolt",
    "stone horn dignatary": "Stonehorn Dignitary",
    "archeomancer": "Archaeomancer",
    "archeomance": "Archaeomancer",
    "Grenade Goblin": "Goblin Grenade",
    "Pilar of Flame": "Pillar of Flame",
    "Elwphant Guide": "Elephant Guide",
    "Scarrgan Pit-Skulk": "Skarrgan Pit-Skulk",
    "Ghazbaen Ogre": "Ghazbán Ogre",
    "fiera gridatempesta": "Stormshriek Feral",
    "Skittering Kitten": "Masked Meower",
    "Wonderweave Aerialist": "Skyward Spider",
    "Patada Selvagem": "Savage Swipe",
    "Vines of Vasrwood": "Vines of Vastwood",
    "confronto Epico": "Epic Confrontation",
    "Hunger of Howlpack": "Hunger of the Howlpack",
}


def is_valid_p12e_deckstats_name(deck_name):
    # A valid name for a deckstats deck has the following format:
    # Archetype Name magic_set_id.revision_id
    tokens = deck_name.rsplit(" ", maxsplit=1)
    # We should now have:
    # [Archetype Name, magic_set_id.revision_id.player_id]
    if not len(tokens) == 2:
        return False
    # archetype = tokens[0]
    deck_id = tokens[1]
    if deck_id.count(".") != 1:
        return False
    p12e_code, deck_number = deck_id.split(".")
    return len(deck_number) == 3


def is_valid_p12e_deck_name(deck_name):
    # A valid name for a deck has the following format:
    # Archetype Name magic_set_id.revision_id.player_id
    tokens = deck_name.rsplit(" ", maxsplit=1)
    # We should now have:
    # [Archetype Name, magic_set_id.revision_id.player_id]
    if not len(tokens) == 2:
        return False
    # archetype = tokens[0]
    deck_id = tokens[1]
    if deck_id.count(".") != 2:
        return False
    p12e_code, deck_number, player_id = deck_id.split(".")
    return len(deck_number) == 3


def fix_card_name(card_name):
    for typo, fix in TYPOS.items():
        card_name = card_name.replace(typo, fix)
    return card_name
