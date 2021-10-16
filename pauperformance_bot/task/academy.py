from pauperformance_bot.service.academy import Academy
from pauperformance_bot.service.mtg.mtggoldfish import MTGGoldfish
from pauperformance_bot.service.pauperformance import Pauperformance
from pauperformance_bot.service.storage.local import Local


def academy_update():
    storage = Local()
    mtggoldfish = MTGGoldfish(storage)
    pauperformance = Pauperformance(storage, mtggoldfish)
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
