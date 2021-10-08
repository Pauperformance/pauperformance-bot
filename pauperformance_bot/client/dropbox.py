from dropbox import Dropbox
from pauperformance_bot.credentials import dropbox_access_token, dropbox_app_key, dropbox_app_secret
from pauperformance_bot.util.log import get_application_logger

log = get_application_logger()


class DropboxService:

    def __init__(self):
        self._service = Dropbox(
            oauth2_access_token=dropbox_access_token,
            app_key=dropbox_app_key,
            app_secret=dropbox_app_secret,
        )

    @property
    def service(self):
        return self._service

    def list_files(self, path, cursor=None):
        if not cursor:
            results = self._service.files_list_folder(path)
        else:
            results = self._service.files_list_folder_continue(cursor)
        items = results.entries
        if not results.has_more:
            return items
        return items + self.list_files(path, results.cursor)

    def create_file(self, name):
        log.info(f"Storing file {name}...")
        results = self._service.files_upload(bytes(), name, mute=True)
        log.info(f"Stored file {name}: {results}")
