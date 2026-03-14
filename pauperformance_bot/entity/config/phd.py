from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class PhDConfig:
    def __init__(
        self,
        *,
        name: str,
        mtgo_name: str | None,
        twitch_login_name: str | None,
        youtube_channel_id: str | None,
        default_youtube_language: str | None,
        discord_id: int | None,
        deckstats_name: str | None,
        deckstats_id: str | None,
    ) -> None:
        self.name = name
        self.mtgo_name = mtgo_name
        self.twitch_login_name = twitch_login_name
        self.youtube_channel_id = youtube_channel_id
        self.default_youtube_language = default_youtube_language
        self.discord_id = discord_id
        self.deckstats_name = deckstats_name
        self.deckstats_id = deckstats_id

    def __hash__(self) -> int:
        return hash(self.name)
