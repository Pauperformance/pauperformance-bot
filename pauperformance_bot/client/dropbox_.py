from dropbox import Dropbox as OfficialDropbox

from pauperformance_bot.constant.dropbox import MYR_DIR_PATH
from pauperformance_bot.credentials import DROPBOX_ACCESS_TOKEN, DROPBOX_APP_KEY, DROPBOX_APP_SECRET
from pauperformance_bot.util.log import get_application_logger

log = get_application_logger()


class Dropbox:

    def __init__(self):
        self._service = OfficialDropbox(
            oauth2_access_token=DROPBOX_ACCESS_TOKEN,
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET,
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

    def create_file(self, name, content=''):
        log.info(f"Storing file {name}...")
        results = self._service.files_upload(content.encode('utf-8'), name, mute=True)
        log.info(f"Stored file {name}: {results}")


if __name__ == '__main__':
    dropbox = Dropbox()
    print(dropbox.list_files(MYR_DIR_PATH))
