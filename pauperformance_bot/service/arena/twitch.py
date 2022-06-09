from twitchAPI import TimePeriod
from twitchAPI.twitch import Twitch

from pauperformance_bot.credentials import (
    TWITCH_APP_CLIENT_ID,
    TWITCH_APP_CLIENT_SECRET,
)
from pauperformance_bot.entity.arena.twitch_user import TwitchUser
from pauperformance_bot.entity.arena.twitch_video import TwitchVideo
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class TwitchService:
    def __init__(
        self,
        myr_client_id=TWITCH_APP_CLIENT_ID,
        myr_client_secret=TWITCH_APP_CLIENT_SECRET,
    ):
        self._service = Twitch(myr_client_id, myr_client_secret)

    def get_user(self, login_name):
        user = self._service.get_users(logins=[login_name])["data"][0]
        return TwitchUser(
            user["id"],
            user["login"],
            user["display_name"],
            user["description"],
        )

    def get_users(self, login_names):
        return [
            TwitchUser(
                user["id"],
                user["login"],
                user["display_name"],
                user["description"],
            )
            for user in self._service.get_users(logins=login_names)["data"]
        ]

    def get_user_videos(self, user_id):
        return [
            TwitchVideo(
                video["id"],
                video["stream_id"],
                video["user_id"],
                video["user_login"],
                video["user_name"],
                video["title"],
                video["description"],
                video["created_at"],
                video["published_at"],
                video["url"],
                video["viewable"],
                video["language"],
                video["duration"],
            )
            for video in self._service.get_videos(
                user_id=user_id,
                first=100,
                period=TimePeriod.MONTH,
            )["data"]
        ]
