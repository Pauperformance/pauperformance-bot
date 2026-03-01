import pickle

from pauperformance_bot.constant.pauperformance.myr import RESOURCES_DIR
from pauperformance_bot.service.academy.data_exporter import AcademyDataExporter
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()

SILVER_DIR = posix_path(RESOURCES_DIR, "silver")
SNAPSHOT_PATH = posix_path(SILVER_DIR, "classifier_snapshot.pkl")


def _get_dpl_classifier():
    """Build a Decklassifier with full service initialization.

    This is intentionally a standalone function (not imported from silver.py)
    because importing silver.py triggers eager classifier initialization
    via ``DPL_SILVER = get_dpl_classifier()`` at module level.
    """
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    exporter = AcademyDataExporter(pauperformance)
    known_decks, _ = exporter._load_mtggoldfish_tournament_training_data()
    other_known_decks, _ = exporter._load_dpl_training_data()
    known_decks += other_known_decks
    return Decklassifier(pauperformance, known_decks)


def build_snapshot(output_path=SNAPSHOT_PATH):
    logger.info("Building classifier snapshot...")

    logger.info("Running full classifier initialization...")
    classifier = _get_dpl_classifier()

    logger.info("Pre-warming reference deck cache...")
    for archetype in classifier.archetypes:
        for reference_deck in archetype.reference_decks:
            if reference_deck not in classifier._decks_cache:
                logger.info(f"Fetching reference deck: {reference_deck}")
                classifier._decks_cache[reference_deck] = (
                    classifier.pauperformance.get_playable_deck(reference_deck)
                )

    logger.info("Extracting artifact land names...")
    artifact_lands = classifier.pauperformance.scryfall.get_legal_artifact_lands()
    artifact_land_names = [c["name"] for c in artifact_lands]

    snapshot = {
        "archetypes": classifier.archetypes,
        "known_decks": classifier.known_decks,
        "decks_cache": classifier._decks_cache,
        "artifact_land_names": artifact_land_names,
    }

    logger.info(f"Serializing snapshot to {output_path}...")
    with open(output_path, "wb") as f:
        pickle.dump(snapshot, f)

    logger.info(
        f"Snapshot built: {len(classifier.archetypes)} archetypes, "
        f"{len(classifier.known_decks)} known decks, "
        f"{len(classifier._decks_cache)} cached reference decks, "
        f"{len(artifact_land_names)} artifact land names."
    )
    return output_path


if __name__ == "__main__":
    build_snapshot()
