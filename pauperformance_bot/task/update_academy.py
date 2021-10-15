from pauperformance_bot.client.academy import Academy
from pauperformance_bot.client.pauperformance import Pauperformance


def update_academy():
    pauperformance = Pauperformance()
    academy = Academy(pauperformance)
    # academy.update_archetypes_index()
    # academy.update_families()
    # academy.update_set_index()
    # academy.update_pauper_pool()
    # academy.update_archetypes()
    academy.update_all()


if __name__ == '__main__':
    update_academy()
