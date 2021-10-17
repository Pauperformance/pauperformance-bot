from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.mtg.archive.local import (
    LocalArchiveService as LocalArchive,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.local import (
    LocalStorageService as LocalStorage,
)


def academy_update(pauperformance):
    academy = AcademyService(pauperformance)
    academy.update_all()


def main():
    storage = LocalStorage()
    archive = LocalArchive()
    pauperformance = PauperformanceService(storage, archive)
    academy_update(pauperformance)


if __name__ == "__main__":
    main()
