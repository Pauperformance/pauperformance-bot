from pauperformance_bot.service.academy import AcademyService

# from pauperformance_bot.service.archive.local import (
#     LocalArchiveService as LocalArchive,
# )
from pauperformance_bot.service.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.dropbox_ import DropboxService

# from pauperformance_bot.service.storage.local import (
#     LocalStorageService as LocalStorage,
# )


def academy_update(pauperformance):
    academy = AcademyService(pauperformance)
    # academy.update_home()
    # academy.update_set_index()
    # academy.update_pauper_pool()
    academy.update_all()
    # academy.update_archetypes()


def main():
    # storage = LocalStorage()
    storage = DropboxService()
    # archive = LocalArchive()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)
    # decks = pauperformance.list_archived_decks()
    # print(len(decks))
    # decks = [
    #     "Atog Shift 612.001.Matteo Mazzola",
    #     "Turbo Slivers 590.001.gannoncd",
    #     "Turbo Slivers 560.001.frucile",
    # ]
    # for d in decks:
    #     pauperformance.delete_deck(d)
    # decks = pauperformance.list_archived_decks()

    # print(pauperformance.get_set_index_by_date("2022-02-21"))
    # pauperformance.import_decks_from_deckstats()
    academy_update(pauperformance)


if __name__ == "__main__":
    main()
