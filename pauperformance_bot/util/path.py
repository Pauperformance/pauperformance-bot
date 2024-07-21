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
    res = unicodedata.normalize("NFKC", name).encode("ASCII").lower()
    res = res.replace("//", "_or_")
    # remove all  except for word characters (letters, digits, and underscores),
    # whitespace characters, and hyphens.
    res = re.sub(r"[^\w\s-]", "", res)
    # replace repeating whitespaces or dashes.
    re.sub(r"[-\s]+", "-", res).strip("-_")
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
