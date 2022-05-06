def is_valid_p12e_deckstats_name(deck_name):
    # A valid name for a deck has the following format:
    # Archetype Name magic_set_id.revision_id.player_id
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
