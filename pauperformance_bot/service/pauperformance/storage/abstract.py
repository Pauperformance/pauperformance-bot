from abc import ABCMeta, abstractmethod
from typing import Any

from pauperformance_bot.constant.pauperformance.myr import (
    STORAGE_DECKS_SUBDIR,
    STORAGE_DECKSTATS_DECKS_SUBDIR,
    STORAGE_MTGGOLDFISH_DECKS_SUBDIR,
    STORAGE_TWITCH_VIDEOS_SUBDIR,
    STORAGE_VIDEOS_SUBDIR,
    STORAGE_YOUTUBE_VIDEOS_SUBDIR,
)


class AbstractStorageService(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _root(self) -> str:
        pass

    @property
    @abstractmethod
    def _dir_separator(self) -> str:
        pass

    @property
    def decks_path(self, decks_subdir: str = STORAGE_DECKS_SUBDIR) -> str:
        return f"{self._root}{self._dir_separator}{decks_subdir}"

    @property
    def deckstats_deck_path(
        self, deckstats_subdir: str = STORAGE_DECKSTATS_DECKS_SUBDIR
    ) -> str:
        return f"{self.decks_path}{self._dir_separator}{deckstats_subdir}"

    @property
    def mtggoldfish_deck_path(
        self, mtggoldfish_subdir: str = STORAGE_MTGGOLDFISH_DECKS_SUBDIR
    ) -> str:
        return f"{self.decks_path}{self._dir_separator}{mtggoldfish_subdir}"

    @property
    def videos_path(self, videos_subdir: str = STORAGE_VIDEOS_SUBDIR) -> str:
        return f"{self._root}{self._dir_separator}{videos_subdir}"

    @property
    def twitch_video_path(
        self, twitch_subdir: str = STORAGE_TWITCH_VIDEOS_SUBDIR
    ) -> str:
        return f"{self.videos_path}{self._dir_separator}{twitch_subdir}"

    @property
    def youtube_video_path(
        self, youtube_subdir: str = STORAGE_YOUTUBE_VIDEOS_SUBDIR
    ) -> str:
        return f"{self.videos_path}{self._dir_separator}{youtube_subdir}"

    @abstractmethod
    def _list_files(self, path: str, cursor: Any = None) -> list[Any]:
        pass

    @abstractmethod
    def create_file(self, name: str, content: str = "") -> None:
        pass

    @abstractmethod
    def get_file(self, name: str) -> Any:
        pass

    @abstractmethod
    def list_imported_deckstats_deck_ids(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_deckstats_deck_names(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_mtggoldfish_deck_ids(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_mtggoldfish_deck_names(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_twitch_videos(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_twitch_videos_ids(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_youtube_videos(self) -> set[str]:
        pass

    @abstractmethod
    def list_imported_youtube_videos_ids(self) -> set[str]:
        pass

    @abstractmethod
    def delete_deck_by_name(self, deck_name: str) -> None:
        pass

    def get_imported_deckstats_deck_key(
        self,
        deckstats_deck_saved_id: str,
        mtggoldfish_deck_id: str,
        deck_name: str,
    ) -> str:
        return (
            f"{self.deckstats_deck_path}"
            f"{self._dir_separator}"
            f"{deckstats_deck_saved_id}>"
            f"{mtggoldfish_deck_id}>"
            f"{deck_name}.txt"
        )

    def get_imported_mtggoldfish_deck_key(
        self,
        mtggoldfish_original_deck_id: str,
        mtggoldfish_archived_deck_id: str,
        deck_name: str,
    ) -> str:
        return (
            f"{self.mtggoldfish_deck_path}"
            f"{self._dir_separator}"
            f"{mtggoldfish_original_deck_id}>"
            f"{mtggoldfish_archived_deck_id}>"
            f"{deck_name}.txt"
        )

    def get_imported_twitch_video_key(
        self,
        video_id: str,
        user_login_name: str,
        language: str,
        date: str,
        deck_name: str,
    ) -> str:
        return (
            f"{self.twitch_video_path}"
            f"{self._dir_separator}"
            f"{video_id}>"
            f"{user_login_name}>"
            f"{language}>"
            f"{date}>"
            f"{deck_name}.txt"
        )

    def get_imported_youtube_video_key(
        self,
        video_id: str,
        channel_title: str,
        language: str,
        date: str,
        deck_name: str,
    ) -> str:
        return (
            f"{self.youtube_video_path}"
            f"{self._dir_separator}"
            f"{video_id}>"
            f"{channel_title}>"
            f"{language}>"
            f"{date}>"
            f"{deck_name}.txt"
        )

    @staticmethod
    def get_imported_deckstats_deck_id_from_key(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_deckstats_deck_name_from_key(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1].split(">")[2][:-4]  # drop .txt

    @staticmethod
    def get_imported_mtggoldfish_deck_id_from_key(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_mtggoldfish_deck_name_from_key(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1].split(">")[2][:-4]  # drop .txt

    @staticmethod
    def get_imported_twitch_video_id_from_key(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_twitch_video(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1][:-4]  # drop .txt

    @staticmethod
    def get_imported_youtube_video_id_from_key(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1].split(">")[0]

    @staticmethod
    def get_imported_youtube_video(key: str) -> str:
        return key.rsplit("/", maxsplit=1)[1][:-4]  # drop .txt
