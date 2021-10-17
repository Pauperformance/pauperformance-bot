from dropbox import Dropbox as OfficialDropbox

from pauperformance_bot.constant.dropbox import MYR_ROOT_DIR
from pauperformance_bot.credentials import (
    DROPBOX_ACCESS_TOKEN,
    DROPBOX_APP_KEY,
    DROPBOX_APP_SECRET,
)
from pauperformance_bot.service.storage.abstract import AbstractStorageService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DropboxService(AbstractStorageService):
    def __init__(self, root_dir=MYR_ROOT_DIR):
        self._root_dir = root_dir
        self._service = OfficialDropbox(
            oauth2_access_token=DROPBOX_ACCESS_TOKEN,
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET,
        )

    @property
    def _root(self):
        return self._root_dir

    @property
    def _dir_separator(self):
        return "/"

    @property
    def service(self):
        return self._service

    def _list_files(self, path, cursor=None):
        if not cursor:
            results = self._service.files_list_folder(path)
        else:
            results = self._service.files_list_folder_continue(cursor)
        items = results.entries
        if not results.has_more:
            return items
        return items + self._list_files(path, results.cursor)

    def create_file(self, name, content=""):
        logger.info(f"Storing file {name}...")
        results = self._service.files_upload(
            content.encode("utf-8"), name, mute=True
        )
        logger.info(f"Stored file {name}: {results}")

    def list_imported_deckstats_deck_ids(self):
        return set(
            self.get_imported_deckstats_deck_id_from_key(file.path_display)
            for file in self._list_files(self.deckstats_deck_path)
        )

    def list_imported_deckstats_deck_names(self):
        return set(
            self.get_imported_deckstats_deck_name_from_key(file.path_display)
            for file in self._list_files(self.deckstats_deck_path)
        )
