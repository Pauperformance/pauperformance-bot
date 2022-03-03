class TwitchUser:
    def __init__(self, user_id, login_name, display_name, description):
        self.user_id = user_id
        self.login_name = login_name
        self.display_name = display_name
        self.description = description

    def __str__(self):
        return (
            f"{self.login_name} ({self.display_name}). "
            f"Id: {self.user_id}. "
            f"Description: {self.description}"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
