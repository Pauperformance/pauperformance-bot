def is_valid_p13e_deckstats_name(deck_name):
    tokens = deck_name.rsplit(' ', maxsplit=1)
    if not len(tokens) == 2:
        return False
    # archetype = tokens[0]
    deck_id = tokens[1]
    if deck_id.count('.') != 1:
        return False
    p13e_code, deck_number = deck_id.split('.')
    return len(p13e_code) == len(deck_number) == 3
