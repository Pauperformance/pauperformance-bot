import json
import os

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import ACADEMY_FILE_SYSTEM
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier
from pauperformance_bot.service.pauperformance.silver.video_classifier import (
    VideoClassifier,
)
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import (
    safe_dump_json_to_file,
)

logger = get_application_logger()


def get_dpl_classifier():
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
    return Decklassifier(pauperformance, ACADEMY_FILE_SYSTEM)


DPL_SILVER = get_dpl_classifier()


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


def classify():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)
    decklassifier = Decklassifier(pauperformance, ACADEMY_FILE_SYSTEM)
    classifier = VideoClassifier(pauperformance, decklassifier)
    classifier.classify_videos()


if __name__ == "__main__":
    # main(
    #     posix_path(TOP_PATH, "dev", "decks-all-tournaments.json"),
    #     posix_path(TOP_PATH, "dev", "decks-all-tournaments-classified.json"),
    # )
    classify()
