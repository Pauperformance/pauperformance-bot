import os
from pathlib import Path

import jsonpickle

jsonpickle.set_preferred_backend("json")
jsonpickle.set_encoder_options("json", sort_keys=True, indent=4)


def posix_path(*args: str) -> str:
    return Path().joinpath(*args).as_posix()


def safe_dump_json_to_file(path, file_name, obj):
    os.makedirs(path, exist_ok=True)
    with open(posix_path(path, file_name), "w") as out_f:
        out_f.write(jsonpickle.encode(obj, make_refs=False, warn=True))


def load_json_from_file(file_path):
    with open(file_path, "r") as in_f:
        return jsonpickle.decode(in_f.read())
