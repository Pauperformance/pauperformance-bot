from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.archive.mtggoldfish import MTGGoldfishArchiveService
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.dropbox_ import DropboxService


def academy_update():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    # update pages
    academy = AcademyService(pauperformance)
    academy.export_all()


def main():
    academy_update()


if __name__ == "__main__":
    main()
