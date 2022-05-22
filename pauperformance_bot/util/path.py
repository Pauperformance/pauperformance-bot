import json
import os
from pathlib import Path


def posix_path(*args: str) -> str:
    return Path().joinpath(*args).as_posix()


def safe_dump_json_to_file(path, file_name, obj):
    os.makedirs(path, exist_ok=True)
    with open(posix_path(path, file_name), "w") as out_f:
        json.dump(obj.__dict__, out_f, sort_keys=True, indent=4)
