from pauperformance_bot.client.academy import Academy


def update_academy():
    academy = Academy()
    # academy.update_archetypes_index()
    # academy.update_set_index()
    # academy.update_pauper_pool()
    # academy.update_archetypes()
    academy.update_all()


if __name__ == '__main__':
    update_academy()
