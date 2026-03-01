from pauperformance_bot.entity.api.archetype import Resource
from pauperformance_bot.entity.config.archetype import ChangelogEntry
from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class Newspauper:
    def __init__(
        self,
        *,
        news: list[Resource],
    ) -> None:
        self.news = news

    def __hash__(self) -> int:
        return hash(self.news)


@auto_repr
@auto_str
class Changelog:
    def __init__(
        self,
        *,
        changes: list[ChangelogEntry],
    ) -> None:
        self.changes = changes

    def __hash__(self) -> int:
        return hash(self.changes)


@auto_repr
@auto_str
class MetaShare:
    def __init__(
        self,
        *,
        mtggolfish_urls: list[str],
        meta_share: float,
        archetype_name: str,
        accuracy: float,
    ) -> None:
        self.mtggolfish_urls = mtggolfish_urls
        self.meta_share = meta_share
        self.archetype_name = archetype_name
        self.accuracy = accuracy

    def __hash__(self) -> int:
        return hash(self.mtggolfish_urls)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, MetaShare):
            return self.meta_share < other.meta_share
        raise ValueError(
            f"Cannot compare instance of MetaShare with instance of {type(other)}"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MetaShare):
            return self.archetype_name == other.archetype_name
        return False


@auto_repr
@auto_str
class Metagame:
    def __init__(
        self,
        *,
        meta_shares: list[MetaShare],
    ) -> None:
        self.meta_shares = meta_shares

    def __hash__(self) -> int:
        return hash(self.meta_shares)


@auto_repr
@auto_str
class DPLDeck:
    def __init__(self, *, identifier: str, archetype: str, accuracy: float) -> None:
        self.identifier = identifier
        self.archetype = archetype
        self.accuracy = accuracy

    def __hash__(self) -> int:
        return hash(self.identifier)


@auto_repr
@auto_str
class DPLMeta:
    def __init__(self, *, name: str, dpl_decks: list[DPLDeck]) -> None:
        self.name = name
        self.dpl_decks = dpl_decks

    @property
    def identifier(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.identifier)
