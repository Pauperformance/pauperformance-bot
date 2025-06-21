from pauperformance_bot.constant.pauperformance.myr import TOP_PATH
from pauperformance_bot.service.academy.data_exporter import AcademyDataExporter
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.util.path import posix_path


def generate_dpl_meta(input_file, output_file):
    # from pauperformance_bot.service.pauperformance.archive.local import (
    #     LocalArchiveService
    # )
    # from pauperformance_bot.service.pauperformance.storage.local import (
    #     LocalStorageService
    # )
    # storage = LocalStorageService()
    # archive = LocalArchiveService()
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    exporter = AcademyDataExporter(pauperformance)
    # TODO: improve
    known_decks, _ = exporter._load_mtggoldfish_tournament_training_data()
    silver = Decklassifier(pauperformance, known_decks)
    silver.get_dpl_metagame(input_file, output_file)


def main(input_file, output_file):
    generate_dpl_meta(input_file, output_file)


def dpl_classifier(environ, start_response):
    """Simplest possible application object"""
    data = b"Hello, World!\n"
    status = "200 OK"
    response_headers = [
        ("Content-type", "text/plain"),
        ("Content-Length", str(len(data))),
    ]
    start_response(status, response_headers)
    return iter([data])


if __name__ == "__main__":
    main(
        posix_path(TOP_PATH, "dev", "decks-all-tournaments.json"),
        posix_path(TOP_PATH, "dev", "decks-all-tournaments-classified.json"),
    )
