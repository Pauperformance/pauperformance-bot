import json
import tempfile

from dropbox import Dropbox as OfficialDropbox
from dropbox import DropboxOAuth2FlowNoRedirect

from pauperformance_bot.constant.dropbox import MYR_ROOT_DIR
from pauperformance_bot.credentials import (
    DROPBOX_APP_KEY,
    DROPBOX_APP_SECRET,
    DROPBOX_REFRESH_TOKEN,
)
from pauperformance_bot.exceptions import StoredFileNotFound
from pauperformance_bot.service.storage.abstract import AbstractStorageService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DropboxService(AbstractStorageService):
    def __init__(
        self,
        root_dir=MYR_ROOT_DIR,
        refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET,
    ):
        self._root_dir = root_dir
        self.app_key = app_key
        self.app_secret = app_secret
        self._service = OfficialDropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret,
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
        results = self._service.files_upload(content.encode("utf-8"), name, mute=True)
        logger.info(f"Stored file {name}: {results}")

    def get_file(self, name):
        logger.info(f"Downloading file {name}...")
        with tempfile.NamedTemporaryFile("w+") as out_f:
            self._service.files_download_to_file(out_f.name, name)
            content = out_f.read()
        logger.info(f"Downloaded file {name}.")
        return json.loads(content)

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

    def list_imported_mtggoldfish_deck_ids(self):
        return set(
            self.get_imported_mtggoldfish_deck_id_from_key(file.path_display)
            for file in self._list_files(self.mtggoldfish_deck_path)
        )

    def list_imported_mtggoldfish_deck_names(self):
        return set(
            self.get_imported_mtggoldfish_deck_name_from_key(file.path_display)
            for file in self._list_files(self.mtggoldfish_deck_path)
        )

    def list_imported_twitch_videos(self):
        return set(
            self.get_imported_twitch_video(file.path_display)
            for file in self._list_files(self.twitch_video_path)
        )

    def list_imported_twitch_videos_ids(self):
        return set(
            self.get_imported_twitch_video_id_from_key(file.path_display)
            for file in self._list_files(self.twitch_video_path)
        )

    def list_imported_youtube_videos(self):
        return set(
            self.get_imported_youtube_video(file.path_display)
            for file in self._list_files(self.youtube_video_path)
        )

    def list_imported_youtube_videos_ids(self):
        return set(
            self.get_imported_youtube_video_id_from_key(file.path_display)
            for file in self._list_files(self.youtube_video_path)
        )

    def delete_deck_by_name(self, deck_name):
        logger.info(f"Deleting file containing {deck_name}...")
        file_path = None
        for file in self._list_files(self.deckstats_deck_path):
            if deck_name in file.name:
                file_path = file.path_display
                break
        if file_path is None:
            raise StoredFileNotFound(f"File not found in storage including {deck_name}")
        logger.info(f"Deleting file {file_path}...")
        self._service.files_delete_v2(file_path)
        logger.info(f"Deleted file containing {deck_name}.")

    def _oauth_interactive_flow(self):
        auth_flow = DropboxOAuth2FlowNoRedirect(
            self.app_key, use_pkce=True, token_access_type="offline"
        )
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print('2. Click "Allow" (you might have to log in first).')
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        oauth_result = auth_flow.finish(auth_code)
        with OfficialDropbox(
            oauth2_refresh_token=oauth_result.refresh_token,
            app_key=self.app_key,
        ) as service:
            service.users_get_current_account()
            print("Successfully set up client!")
