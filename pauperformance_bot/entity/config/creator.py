from typing import Optional

from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class CreatorConfig:
    def __init__(
        self,
        *,
        name: str,
        mtgo_name: Optional[str],
        mtgo_name2: Optional[str],
        twitch_login_name: Optional[str],
        youtube_channel_id: Optional[str],
    ):
        self.name: str = name
        self.mtgo_name: Optional[str] = mtgo_name
        self.mtgo_name2: Optional[str] = mtgo_name2
        self.twitch_login_name: Optional[str] = twitch_login_name
        self.youtube_channel_id: Optional[str] = youtube_channel_id

    def __hash__(self) -> int:
        return hash(self.name)
