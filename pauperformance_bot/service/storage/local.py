from os import listdir, remove
from os.path import isfile, join, sep

from pauperformance_bot.constant.myr import STORAGE_DIR
from pauperformance_bot.exceptions import StoredFileNotFound
from pauperformance_bot.service.storage.abstract import AbstractStorageService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class LocalStorageService(AbstractStorageService):
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
        logger.info(f"Storing file {name}...")
        with open(name, "w", encoding="utf-8") as out_f:
            out_f.write(content)
        logger.info(f"Stored file {name}.")

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

    def delete_deck_by_name(self, deck_name):
        logger.info(f"Deleting file containing {deck_name}...")
        file_path = None
        for file in self._list_files(self.deckstats_deck_path):
            if deck_name in file:
                file_path = file
                break
        if file_path is None:
            raise StoredFileNotFound(
                f"File not found in storage including {deck_name}"
            )
        logger.info(f"Deleting file {file_path}...")
        remove(file_path)
        logger.info(f"Deleted file containing {deck_name}.")
