from typing import Optional

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
        creator_name: str,
        date: str,
        archetype: str,
        video_id: str,
        deck_name: Optional[str],
        is_short: bool,
    ):
        self.name: str = name
        self.link: str = link
        self.language: str = language
        self.creator_name: str = creator_name
        self.date: str = date
        self.archetype: str = archetype
        self.video_id: str = video_id
        self.deck_name: Optional[str] = deck_name
        self.is_short: bool = is_short

    def __hash__(self):
        return hash(self.video_id)
