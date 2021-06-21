from pauperformance_bot.client.pauperformance import Pauperformance


def date():
    usa_date = "2019-03-25"
    pauperformance = Pauperformance()
    set_index = pauperformance.get_set_index()
    cards_index = pauperformance.get_pauper_cards_incremental_index()
    latest_set = [
        s for s in set_index
        if s['date'] <= usa_date and len(cards_index.get(s['p12e_code'])) > 0
    ][-1]
    print(
        f"{latest_set['p12e_code']} "
        f"({latest_set['name']} @ {latest_set['date']})"
    )


if __name__ == '__main__':
    date()
