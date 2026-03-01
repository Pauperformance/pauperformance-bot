from pauperformance_bot.entity.arena.indexable_video import IndexableVideo
from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class TwitchVideo(IndexableVideo):
    def __init__(
        self,
        video_id: str,
        stream_id: str,
        user_id: str,
        user_login_name: str,
        user_display_name: str,
        title: str,
        description: str,
        created_at: str,
        published_at: str,
        url: str,
        viewable: str,
        language: str,
        duration: str,
    ) -> None:
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
