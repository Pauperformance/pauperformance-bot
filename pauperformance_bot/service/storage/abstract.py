from abc import ABCMeta, abstractmethod

from pauperformance_bot.constant.myr import (
    STORAGE_DECKS_SUBDIR,
    STORAGE_DECKSTATS_DECKS_SUBDIR,
    STORAGE_TWITCH_VIDEOS_SUBDIR,
    STORAGE_VIDEOS_SUBDIR,
)


class AbstractStorageService(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _root(self):
        pass

    @property
    @abstractmethod
    def _dir_separator(self):
        pass

    @property
    def decks_path(self, decks_subdir=STORAGE_DECKS_SUBDIR):
        return f"{self._root}{self._dir_separator}{decks_subdir}"

    @property
    def deckstats_deck_path(
        self, deckstats_subdir=STORAGE_DECKSTATS_DECKS_SUBDIR
    ):
        return f"{self.decks_path}{self._dir_separator}{deckstats_subdir}"

    @property
    def videos_path(self, videos_subdir=STORAGE_VIDEOS_SUBDIR):
        return f"{self._root}{self._dir_separator}{videos_subdir}"

    @property
    def twitch_video_path(self, twitch_subdir=STORAGE_TWITCH_VIDEOS_SUBDIR):
        return f"{self.videos_path}{self._dir_separator}{twitch_subdir}"

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

    @abstractmethod
    def list_imported_twitch_videos(self):
        pass

    @abstractmethod
    def list_imported_twitch_videos_ids(self):
        pass

    @abstractmethod
    def delete_deck_by_name(self, deck_name):
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

    def get_imported_twitch_video_key(
        self,
        video_id,
        user_login_name,
        language,
        date,
        deck_name,
    ):
        return (
            f"{self.twitch_video_path}"
            f"{self._dir_separator}"
            f"{video_id}>"
            f"{user_login_name}>"
            f"{language}>"
            f"{date}>"
            f"{deck_name}.txt"
        )

    @staticmethod
    def get_imported_deckstats_deck_id_from_key(key):
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_deckstats_deck_name_from_key(key):
        return key.rsplit("/", maxsplit=1)[1].split(">")[2][:-4]  # drop .txt

    @staticmethod
    def get_imported_twitch_video_id_from_key(key):
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_twitch_video(key):
        return key.rsplit("/", maxsplit=1)[1][:-4]  # drop .txt
