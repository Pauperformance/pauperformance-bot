from pauperformance_bot.entity.arena.indexable_video import IndexableVideo
from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class YouTubeVideo(IndexableVideo):
    def __init__(
        self,
        video_id,  # YouTube internals
        etag,
        content_video_id,  # as displayed in the URL
        published_at,
        channel_id,
        channel_title,
        description,
        playlist_id,
        position,
        created_at,
        title,
        privacy_status,
        url,
        language,
    ):
        super().__init__(description)
        self.video_id = video_id
        self.etag = etag
        self.content_video_id = content_video_id
        self.published_at = published_at
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.playlist_id = playlist_id
        self.position = position
        self.created_at = created_at
        self.title = title
        self.privacy_status = privacy_status
        self.url = url
        self.language = language

    def __hash__(self) -> int:
        return hash(self.video_id)
