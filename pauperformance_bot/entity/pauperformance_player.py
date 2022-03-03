class PauperformancePlayer:
    def __init__(
        self,
        name,
        mtgo_name,
        deckstats_name,
        deckstats_id,
        telegram_id,
        twitch_login_name,
    ):
        self.name = name
        self.mtgo_name = mtgo_name
        self.deckstats_name = deckstats_name
        self.deckstats_id = deckstats_id
        self.telegram_id = telegram_id
        self.twitch_login_name = twitch_login_name
