from typing import Optional

from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class PhDConfig:
    def __init__(
        self,
        *,
        name: str,
        mtgo_name: Optional[str],
        twitch_login_name: Optional[str],
        youtube_channel_id: Optional[str],
        default_youtube_language: Optional[str],
        discord_id: Optional[int],
        deckstats_name: Optional[str],
        deckstats_id: Optional[str],
    ):
        self.name: str = name
        self.mtgo_name: Optional[str] = mtgo_name
        self.twitch_login_name: Optional[str] = twitch_login_name
        self.youtube_channel_id: Optional[str] = youtube_channel_id
        self.default_youtube_language: Optional[str] = default_youtube_language
        self.discord_id: Optional[int] = discord_id
        self.deckstats_name: Optional[str] = deckstats_name
        self.deckstats_id: Optional[str] = deckstats_id

    def __hash__(self) -> int:
        return hash(self.name)
