from typing import Optional

from pauperformance_bot.util.entities import auto_repr, auto_str


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
        deck_name: Optional[str],
    ):
        self.name: str = name
        self.link: str = link
        self.language: str = language
        self.phd_name: str = phd_name
        self.date: str = date
        self.archetype: str = archetype
        self.video_id: str = video_id
        self.deck_name: Optional[str] = deck_name

    def __hash__(self):
        return hash(self.video_id)
