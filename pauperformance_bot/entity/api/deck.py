from typing import Optional

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
    ):
        self.name: str = name
        self.url: str = url
        self.archetype: str = archetype
        self.set_name: str = set_name
        self.set_date: str = set_date
        self.legal: bool = legal

    def __hash__(self):
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
        tabletop_price: Optional[int],
        mtgo_price: Optional[int],
        tournament_id: str,
        tournament_name: str,
        tournament_date: str,
    ):
        self.url: str = url
        self.archetype: str = archetype
        self.place: str = place
        self.pilot: str = pilot
        self.tabletop_price: Optional[int] = tabletop_price
        self.mtgo_price: Optional[int] = mtgo_price
        self.tournament_id: str = tournament_id
        self.tournament_name: str = tournament_name
        self.tournament_date: str = tournament_date

    @property
    def identifier(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[-1]

    def __hash__(self):
        return hash(self.identifier)
