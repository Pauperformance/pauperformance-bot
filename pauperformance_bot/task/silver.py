import json
import os

import jsonpickle

from pauperformance_bot.constant.pauperformance.myr import RESOURCES_DIR, TOP_PATH
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import (
    posix_path,
    safe_dump_json_to_file,
)

logger = get_application_logger()

# Path to pre-built snapshot (see build_snapshot.py)
SNAPSHOT_PATH = posix_path(RESOURCES_DIR, "silver", "classifier_snapshot.pkl")


def get_dpl_classifier():
    from pauperformance_bot.service.academy.data_exporter import AcademyDataExporter
    from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
        MTGGoldfishArchiveService,
    )
    from pauperformance_bot.service.pauperformance.pauperformance import (
        PauperformanceService,
    )
    from pauperformance_bot.service.pauperformance.storage.dropbox_ import (
        DropboxService,
    )

    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    exporter = AcademyDataExporter(pauperformance)
    known_decks, _ = exporter._load_mtggoldfish_tournament_training_data()
    other_known_decks, _ = exporter._load_dpl_training_data()
    known_decks += other_known_decks
    return Decklassifier(pauperformance, known_decks)


def load_dpl_classifier():
    if os.path.exists(SNAPSHOT_PATH):
        logger.info(f"Loading classifier from snapshot: {SNAPSHOT_PATH}")
        return Decklassifier.from_snapshot(SNAPSHOT_PATH)
    logger.warning(
        f"Snapshot not found at {SNAPSHOT_PATH}. "
        f"Falling back to full initialization (this will be slow)."
    )
    return get_dpl_classifier()


DPL_SILVER = load_dpl_classifier()


def generate_dpl_meta(data, name="DPL metagame"):
    return DPL_SILVER.get_dpl_metagame(data, name=name)


def main(input_file, output_file):
    logger.info(f"Getting DPL decks from {input_file}...")
    data = json.load(open(input_file))
    dpl_meta = generate_dpl_meta(data, name=input_file)
    try:
        out_dir, out_file = output_file.rsplit(os.path.sep, maxsplit=1)
    except ValueError:
        out_dir = os.getcwd()
        out_file = output_file
    safe_dump_json_to_file(out_dir, out_file, dpl_meta)
    logger.info(f"Stored DPL meta in {output_file}...")


def dpl_classifier(environ, start_response):
    try:
        method = environ["REQUEST_METHOD"]
        if method != "POST":
            start_response(
                "405 Method Not Allowed", [("Content-Type", "application/json")]
            )
            return [json.dumps({"error": "Method not allowed"}).encode("utf-8")]
        try:
            request_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            request_length = 0
        request_body = environ["wsgi.input"].read(request_length)
        data = json.loads(request_body.decode("utf-8"))
        response = generate_dpl_meta(data)
        response = json.loads(jsonpickle.encode(response, make_refs=False, warn=True))
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(response).encode("utf-8")]
    except Exception as e:
        start_response(
            "500 Internal Server Error", [("Content-Type", "application/json")]
        )
        return [json.dumps({"error": str(e)}).encode("utf-8")]


if __name__ == "__main__":
    main(
        posix_path(TOP_PATH, "dev", "decks-all-tournaments.json"),
        posix_path(TOP_PATH, "dev", "decks-all-tournaments-classified.json"),
    )
