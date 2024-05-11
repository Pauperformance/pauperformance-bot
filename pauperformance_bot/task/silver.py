from pauperformance_bot.constant.pauperformance.myr import TOP_PATH
from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.academy.data_exporter import AcademyDataExporter
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver import SilverService
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.util.path import posix_path


def generate_dpl_meta(input_file, output_file):
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    academy = AcademyService(pauperformance)
    exporter = AcademyDataExporter(academy)
    # TODO: improve
    known_decks, _ = exporter._load_mtggoldfish_tournament_training_data()
    silver = SilverService(pauperformance, known_decks)
    silver.get_dpl_metagame(input_file, output_file)


def main(input_file, output_file):
    generate_dpl_meta(input_file, output_file)


if __name__ == "__main__":
    main(
        posix_path(
            TOP_PATH, "dev", "Dutch Pauper League – 3° Leg – 2024 - Command Tower.csv"
        ),
        posix_path(TOP_PATH, "dev", "dpl_meta.json"),
    )
