from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.academy.data_exporter import AcademyDataExporter
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService


def academy_update():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    # export data
    academy = AcademyService(pauperformance)
    exporter = AcademyDataExporter(academy)
    exporter.export_all()


def main():
    academy_update()


if __name__ == "__main__":
    main()
