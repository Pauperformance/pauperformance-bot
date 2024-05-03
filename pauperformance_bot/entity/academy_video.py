from pauperformance_bot.util.decorators import auto_repr, auto_str


# TODO: try to get rid of this class and just use the API counterpart (Video)
@auto_repr
@auto_str
class AcademyVideo:
    def __init__(
        self,
        video_id,
        user_name,
        title,
        language,
        published_at,
        deck_name,
        archetype,
        phd,
        url,
        fa_icon,
    ):
        self.video_id = video_id
        self.user_name = user_name
        self.title = title
        self.language = language
        self.published_at = published_at
        self.deck_name = deck_name
        self.archetype = archetype
        self.phd = phd
        self.url = url
        self.fa_icon = fa_icon

    def __hash__(self) -> int:
        return hash(self.video_id)
