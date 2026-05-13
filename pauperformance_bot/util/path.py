import os
import re
import unicodedata
from pathlib import Path

import jsonpickle

jsonpickle.set_preferred_backend("json")
jsonpickle.set_encoder_options("json", sort_keys=True, indent=4)


def safe_posix_path(name: str) -> str:
    """Converts string to ASCII. Removes characters that aren't alphanumerics,
    underscores, or hyphens. Converts to lowercase. Converts '//' to '_or_'.
    Converts spaces or repeated dashes to single dashes. Also strips leading and
    trailing whitespace, dashes, and underscores."""
    res = (
        unicodedata.normalize("NFKD", name)
        .encode("ASCII", errors="ignore")
        .decode("ASCII")
    )
    res = res.lower().replace("//", "_or_")
    res = re.sub(r"[^\w\s-]", "", res)
    res = re.sub(r"[-\s]+", "-", res).strip("-_")
    return res


def posix_path(*args: str) -> str:
    return Path().joinpath(*args).as_posix()


def safe_dump_json_to_file(path, file_name, obj):
    os.makedirs(path, exist_ok=True)
    with open(posix_path(path, file_name), "w") as out_f:
        out_f.write(jsonpickle.encode(obj, make_refs=False, warn=True))


def load_json_from_file(file_path):
    with open(file_path, "r") as in_f:
        return jsonpickle.decode(in_f.read())
