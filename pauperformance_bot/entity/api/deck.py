from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class Deck:
    def __init__(
        self,
        *,
        name: str,
        url: str,
        archetype: str,
        set_name: str,
        set_date: str,
        legal: bool,
    ):
        self.name: str = name
        self.url: str = url
        self.archetype: str = archetype
        self.set_name: str = set_name
        self.set_date: str = set_date
        self.legal: bool = legal

    def __hash__(self):
        return hash(self.name)
