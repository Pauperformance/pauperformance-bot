from pauperformance_bot.util.decorators import auto_repr, auto_str


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
    ) -> None:
        self.name = name
        self.url = url
        self.archetype = archetype
        self.set_name = set_name
        self.set_date = set_date
        self.legal = legal

    def __hash__(self) -> int:
        return hash(self.name)


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
        tabletop_price: int | None,
        mtgo_price: int | None,
        tournament_id: str,
        tournament_name: str,
        tournament_date: str,
    ) -> None:
        self.url = url
        self.archetype = archetype
        self.place = place
        self.pilot = pilot
        self.tabletop_price = tabletop_price
        self.mtgo_price = mtgo_price
        self.tournament_id = tournament_id
        self.tournament_name = tournament_name
        self.tournament_date = tournament_date

    @property
    def identifier(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[-1]

    def __hash__(self) -> int:
        return hash(self.identifier)
