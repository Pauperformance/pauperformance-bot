from abc import ABCMeta, abstractmethod


class Storage(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _root(self):
        pass

    @property
    @abstractmethod
    def _dir_separator(self):
        pass

    @property
    def decks_path(self):
        return f"{self._root}{self._dir_separator}decks"

    @property
    def deckstats_deck_path(self):
        return f"{self.decks_path}{self._dir_separator}deckstats"

    @property
    def mtggoldfish_deck_path(self):
        return f"{self.decks_path}{self._dir_separator}mtggoldfish"

    @abstractmethod
    def _list_files(self, path, cursor=None):
        pass

    @abstractmethod
    def create_file(self, name, content=""):
        pass

    @abstractmethod
    def list_imported_deckstats_deck_ids(self):
        pass

    @abstractmethod
    def list_imported_deckstats_deck_names(self):
        pass

    def get_imported_deckstats_deck_key(
        self,
        deckstats_deck_saved_id,
        mtggoldfish_deck_id,
        deck_name,
    ):
        return (
            f"{self.deckstats_deck_path}"
            f"{self._dir_separator}"
            f"{deckstats_deck_saved_id}>"
            f"{mtggoldfish_deck_id}>"
            f"{deck_name}.txt"
        )

    @staticmethod
    def get_imported_deckstats_deck_id_from_key(key):
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_deckstats_deck_name_from_key(key):
        return key.rsplit("/", maxsplit=1)[1].split(">")[2][:-4]  # drop .txt
