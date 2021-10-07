from pauperformance_bot.client.academy import Academy


def date_deck(usa_date):
    academy = Academy()
    cards_index = academy.get_pauper_cards_incremental_index()
    return [
        s for s in academy.set_index.values()
        if s['date'] <= usa_date and len(cards_index.get(s['p12e_code'])) > 0
    ][-1]


if __name__ == '__main__':
    latest_set = date_deck("2018-03-30")
    print(
        f"{latest_set['p12e_code']} "
        f"({latest_set['name']} @ {latest_set['date']})"
    )
