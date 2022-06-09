from pyyoutube import Api

from pauperformance_bot.constant.arena.youtube import YOUTUBE_VIDEO_URL
from pauperformance_bot.constant.pauperformance.myr import VIDEO_LANGUAGE_TAG
from pauperformance_bot.credentials import YOUTUBE_API_KEY
from pauperformance_bot.entity.arena.youtube_video import YouTubeVideo
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class YouTubeService:
    def __init__(
        self,
        myr_client_id=YOUTUBE_API_KEY,
    ):
        self._service = Api(api_key=myr_client_id)

    def get_channel_info(self, channel_id):
        return self._service.get_channel_info(channel_id=channel_id)

    def get_video(self, video_id):
        video_by_id = self._service.get_video_by_id(video_id=video_id)
        return video_by_id

    def list_playlists(self, channel_id):
        return self._service.get_playlists(channel_id=channel_id, count=None)

    def list_playlist_videos(self, playlist_id):
        return self._service.get_playlist_items(
            playlist_id=playlist_id,
            count=None,
        ).items

    def get_channel_videos(self, channel_id, default_language) -> list[YouTubeVideo]:
        channel = self.get_channel_info(channel_id)
        uploads = channel.items[0].contentDetails.relatedPlaylists.uploads
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
                self.get_video_language(
                    video.snippet.description,
                    default_language,
                ),
            )
            for video in self.list_playlist_videos(uploads)
        ]

    @staticmethod
    def get_video_language(video_description, default_language):
        language = None
        for line in video_description.split("\n"):
            line = line.strip()
            if line.lower().startswith(VIDEO_LANGUAGE_TAG.lower()):
                logger.debug(f"Extracting video language from line:\n{line}")
                language = line[len(VIDEO_LANGUAGE_TAG) :]
                logger.debug(f"Pairing video to language {language}")
                break
        if not language:
            language = default_language
        return language
