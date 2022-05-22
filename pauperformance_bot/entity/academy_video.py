from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class AcademyVideo:
    def __init__(
        self,
        video_id,
        user_name,
        language,
        published_at,
        deck_name,
        url,
        fa_icon,
    ):
        self.video_id = video_id
        self.user_name = user_name
        self.language = language
        self.published_at = published_at
        self.deck_name = deck_name
        self.url = url
        self.fa_icon = fa_icon

    def __hash__(self) -> int:
        return hash(self.video_id)
