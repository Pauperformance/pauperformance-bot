from pauperformance_bot.service.academy import Academy
from pauperformance_bot.service.mtg.archive.local import Local as LocalArchive
from pauperformance_bot.service.pauperformance import Pauperformance
from pauperformance_bot.service.storage.local import Local as LocalStorage


def academy_update(pauperformance):
    academy = Academy(pauperformance)
    academy.update_all()


def main():
    storage = LocalStorage()
    archive = LocalArchive()
    pauperformance = Pauperformance(storage, archive)
    academy_update(pauperformance)


if __name__ == "__main__":
    main()
