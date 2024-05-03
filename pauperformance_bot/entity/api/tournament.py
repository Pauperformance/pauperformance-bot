from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class Tournament:
    def __init__(self, *, url: str, name: str, date: str, deck_ids: list[str]):
        self.url: str = url
        self.name: str = name
        self.date: str = date
        self.deck_ids: list[str] = deck_ids

    @property
    def identifier(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[-1]

    def __hash__(self):
        return hash(self.identifier)
