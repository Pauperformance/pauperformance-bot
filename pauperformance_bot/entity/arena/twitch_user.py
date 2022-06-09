from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class TwitchUser:
    def __init__(self, user_id, login_name, display_name, description):
        self.user_id = user_id
        self.login_name = login_name
        self.display_name = display_name
        self.description = description

    def __hash__(self) -> int:
        return hash(self.user_id)
