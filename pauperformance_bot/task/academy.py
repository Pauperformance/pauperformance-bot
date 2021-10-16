from pauperformance_bot.client.academy import Academy
from pauperformance_bot.client.pauperformance import Pauperformance


def academy_update():
    pauperformance = Pauperformance()
    academy = Academy(pauperformance)
    # academy.update_archetypes_index()
    # academy.update_families()
    # academy.update_set_index()
    # academy.update_pauper_pool()
    # academy.update_archetypes()
    academy.update_dev()
    # academy.update_all()


if __name__ == "__main__":
    academy_update()
