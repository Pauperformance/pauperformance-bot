from pauperformance_bot.entity.arena.indexable_video import IndexableVideo
from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class TwitchVideo(IndexableVideo):
    def __init__(
        self,
        video_id,
        stream_id,
        user_id,
        user_login_name,
        user_display_name,
        title,
        description,
        created_at,
        published_at,
        url,
        viewable,
        language,
        duration,
    ):
        super().__init__(description)
        self.video_id = video_id
        self.stream_id = stream_id
        self.user_id = user_id
        self.user_login_name = user_login_name
        self.user_display_name = user_display_name
        self.title = title
        self.created_at = created_at
        self.published_at = published_at
        self.url = url
        self.viewable = viewable
        self.language = language
        self.duration = duration

    def __hash__(self) -> int:
        return hash(self.video_id)
