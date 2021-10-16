from os import listdir
from os.path import isfile, join, sep

from pauperformance_bot.constant.myr import STORAGE_DIR
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard
from pauperformance_bot.service.storage.abstract import Storage
from pauperformance_bot.util.log import get_application_logger

log = get_application_logger()


class Local(Storage):
    def __init__(self, root_dir=STORAGE_DIR):
        self._root_dir = root_dir

    @property
    def _root(self):
        return self._root_dir

    @property
    def _dir_separator(self):
        return sep

    def _list_files(self, path, cursor=None):
        return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    def create_file(self, name, content=""):
        log.info(f"Storing file {name}...")
        with open(name, "w", encoding="utf-8") as out_f:
            out_f.write(content)
        log.info(f"Stored file {name}.")

    def list_imported_deckstats_deck_ids(self):
        return set(
            self.get_imported_deckstats_deck_id_from_key(file)
            for file in self._list_files(self.deckstats_deck_path)
        )

    def list_imported_deckstats_deck_names(self):
        return set(
            self.get_imported_deckstats_deck_name_from_key(file)
            for file in self._list_files(self.deckstats_deck_path)
        )


if __name__ == "__main__":
    storage = Local()
    key = storage.get_imported_deckstats_deck_key(
        "2059767",
        "4351760",
        "Aristocrats 676.001.MrEvilEye | Modern Horizons 2 (mh2)",
    )
    main = [PlayedCard(4, "Island"), PlayedCard(4, "Swamp")]
    sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    deck = PlayableDeck(main, sideboard)
    # storage.create_file(key, str(deck))
    print(storage.list_imported_deckstats_deck_ids())
    print(storage.list_imported_deckstats_deck_names())
