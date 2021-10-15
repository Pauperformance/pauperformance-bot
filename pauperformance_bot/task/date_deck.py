from pauperformance_bot.client.pauperformance import Pauperformance


def date_deck(usa_date):
    pauperformance = Pauperformance()
    return pauperformance.get_set_index_by_date(usa_date)


if __name__ == "__main__":
    latest_set = date_deck("2018-03-30")
    print(
        f"{latest_set['p12e_code']} "
        f"({latest_set['name']} @ {latest_set['date']})"
    )
