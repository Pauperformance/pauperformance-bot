from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class Video:
    def __init__(
        self,
        *,
        name: str,
        link: str,
        language: str,
        phd_name: str,
        date: str,
        archetype: str,
        video_id: str,
        deck_name: str | None,
    ) -> None:
        self.name = name
        self.link = link
        self.language = language
        self.phd_name = phd_name
        self.date = date
        self.archetype = archetype
        self.video_id = video_id
        self.deck_name = deck_name

    def __hash__(self) -> int:
        return hash(self.video_id)
