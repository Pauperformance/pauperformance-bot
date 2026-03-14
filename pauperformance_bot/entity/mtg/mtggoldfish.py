from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class MTGGoldfishTournamentSearchResult:
    def __init__(self, *, url: str, name: str, date: str) -> None:
        self.url = url
        self.name = name
        self.date = date

    @property
    def identifier(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[-1]

    def __hash__(self) -> int:
        return hash(self.identifier)
