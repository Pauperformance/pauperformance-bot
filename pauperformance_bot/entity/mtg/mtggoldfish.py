from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class MTGGoldfishTournamentSearchResult:
    def __init__(self, *, url: str, name: str, date: str):
        self.url: str = url
        self.name: str = name
        self.date: str = date

    @property
    def identifier(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[-1]

    def __hash__(self):
        return hash(self.identifier)


@auto_repr
@auto_str
class MTGGoldfishTournamentDeck:
    def __init__(
        self,
        *,
        url: str,
        archetype: str,
        place: str,
        pilot: str,
        tabletop_price: int,
        mtgo_price: int,
    ):
        self.url: str = url
        self.archetype: str = archetype
        self.place: str = place
        self.pilot: str = pilot
        self.tabletop_price: int = tabletop_price
        self.mtgo_price: int = mtgo_price

    @property
    def identifier(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[-1]

    def __hash__(self):
        return hash(self.identifier)
