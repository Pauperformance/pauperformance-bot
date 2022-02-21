import pickle

from pauperformance_bot.constant.myr import TOP_PATH
from pauperformance_bot.util.path import posix_path


def explore_last_set_index():
    last_set_index_file = posix_path(
        TOP_PATH.as_posix(), "resources", "last_set_index.pkl"
    )
    with open(last_set_index_file, "rb") as index_f:
        set_index = pickle.load(index_f)
    known_sets = {s["scryfall_code"] for s in set_index.values()}
    print(known_sets)
    p12e_code = max(set_index.keys()) + 1
    print(p12e_code)


if __name__ == "__main__":
    explore_last_set_index()
