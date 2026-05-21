from datetime import datetime, timezone

import requests
from pyyoutube import Api
from requests_oauthlib import OAuth2Session

from pauperformance_bot.constant.arena.youtube import (
    YOUTUBE_OAUTH_TOKEN_URL,
    YOUTUBE_VIDEO_URL,
)
from pauperformance_bot.credentials import (
    GOOGLE_OAUTH_CLIENT_SECRET,
    GOOGLE_OAUTH_ID_CLIENT,
    GOOGLE_OAUTH_REFRESH_TOKEN,
    YOUTUBE_API_KEY,
)
from pauperformance_bot.entity.arena.youtube_video import YouTubeVideo
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class YouTubeService:
    def __init__(
        self,
        myr_client_id=YOUTUBE_API_KEY,
        oauth_client_id=GOOGLE_OAUTH_ID_CLIENT,
        oauth_client_secret=GOOGLE_OAUTH_CLIENT_SECRET,
        oauth_refresh_token=GOOGLE_OAUTH_REFRESH_TOKEN,
    ):
        self._service = Api(api_key=myr_client_id)
        self._oauth_session = OAuth2Session(
            client_id=oauth_client_id,
            token={
                "access_token": "",
                "refresh_token": oauth_refresh_token,
                "token_type": "Bearer",
                "expires_in": -1,
            },
            auto_refresh_url=YOUTUBE_OAUTH_TOKEN_URL,
            auto_refresh_kwargs={
                "client_id": oauth_client_id,
                "client_secret": oauth_client_secret,
            },
            token_updater=lambda token: None,
        )

    def get_channel_info(self, channel_id):
        return self._service.get_channel_info(channel_id=channel_id)

    def get_video(self, video_id):
        video_by_id = self._service.get_video_by_id(video_id=video_id)
        return video_by_id

    def list_playlists(self, channel_id):
        return self._service.get_playlists(channel_id=channel_id, count=None)

    def list_playlist_videos(self, playlist_id, since=None):
        if since is None:
            return self._service.get_playlist_items(
                playlist_id=playlist_id,
                count=None,
            ).items

        items = []
        page_token = None
        while True:
            response = self._service.get_playlist_items(
                playlist_id=playlist_id,
                count=50,
                limit=50,
                page_token=page_token,
            )
            for item in response.items or []:
                if (
                    datetime.strptime(
                        item.contentDetails.videoPublishedAt, "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=timezone.utc)
                    < since
                ):
                    return items
                items.append(item)
            page_token = response.nextPageToken
            if not page_token:
                break
        return items

    def get_channel_videos(self, channel_id, since=None) -> list[YouTubeVideo]:
        channel = self.get_channel_info(channel_id)
        uploads = channel.items[0].contentDetails.relatedPlaylists.uploads
        videos = self.list_playlist_videos(uploads, since=since)

        video_ids = [item.contentDetails.videoId for item in videos]
        default_languages = self._get_default_audio_languages(video_ids)

        return [
            YouTubeVideo(
                video.id,
                video.etag,
                video.contentDetails.videoId,
                video.contentDetails.videoPublishedAt,
                video.snippet.channelId,
                video.snippet.channelTitle,
                video.snippet.description,
                video.snippet.playlistId,
                video.snippet.position,
                video.snippet.publishedAt,
                video.snippet.title,
                video.status.privacyStatus,
                f"{YOUTUBE_VIDEO_URL}{video.contentDetails.videoId}",
                default_languages.get(video.contentDetails.videoId)
                or self._get_language_from_captions(video.contentDetails.videoId)
                or "Unknown",
                self._is_short(video.contentDetails.videoId),
            )
            for video in videos
        ]

    def _is_short(self, video_id: str) -> bool:
        try:
            resp = requests.head(
                f"https://www.youtube.com/shorts/{video_id}",
                allow_redirects=True,
                timeout=10,
            )
            return "/shorts/" in resp.url
        except Exception:
            logger.debug(f"Could not determine if {video_id} is a Short.")
            return False

    def _get_default_audio_languages(self, video_ids):
        languages = {}
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i : i + 50]
            try:
                response = self._service.get_video_by_id(
                    video_id=batch, parts=["snippet"]
                )
                for item in response.items or []:
                    lang = item.snippet.defaultAudioLanguage
                    if lang:
                        languages[item.id] = lang
            except Exception:
                logger.debug(
                    f"Could not retrieve defaultAudioLanguage for batch {batch}."
                )
        return languages

    def _get_language_from_captions(self, video_id):
        try:
            response = self._oauth_session.get(
                "https://www.googleapis.com/youtube/v3/captions",
                params={"part": "snippet", "videoId": video_id},
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            if items:
                manual = [i for i in items if i["snippet"]["trackKind"] != "asr"]
                track = (manual or items)[0]
                return track["snippet"]["language"]
        except Exception:
            logger.debug(f"Captions API unavailable for {video_id}.")
        return None
