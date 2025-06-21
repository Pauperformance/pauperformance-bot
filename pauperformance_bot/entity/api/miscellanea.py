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
    ):
        self.news: list[Resource] = news

    def __hash__(self):
        return hash(self.news)


@auto_repr
@auto_str
class Changelog:
    def __init__(
        self,
        *,
        changes: list[ChangelogEntry],
    ):
        self.changes: list[ChangelogEntry] = changes

    def __hash__(self):
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
    ):
        self.mtggolfish_urls: list[str] = mtggolfish_urls
        self.meta_share: float = meta_share
        self.archetype_name: str = archetype_name
        self.accuracy: float = accuracy

    def __hash__(self):
        return hash(self.mtggolfish_urls)

    def __lt__(self, other):
        if isinstance(other, MetaShare):
            return self.meta_share < other.meta_share
        raise ValueError(
            f"Cannot compare instance of MetaShare with instance of {type(other)}"
        )

    def __eq__(self, other):
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
    ):
        self.meta_shares: list[MetaShare] = meta_shares

    def __hash__(self):
        return hash(self.meta_shares)


@auto_repr
@auto_str
class DPLDeck:
    def __init__(self, *, identifier: str, archetype: str, accuracy: float):
        self.identifier = identifier
        self.archetype = archetype
        self.accuracy = accuracy

    def __hash__(self):
        return hash(self.identifier)


@auto_repr
@auto_str
class DPLMeta:
    def __init__(self, *, name: str, dpl_decks: list[DPLDeck]):
        self.name = name
        self.dpl_decks: list[DPLDeck] = dpl_decks

    @property
    def identifier(self) -> str:
        return self.name

    def __hash__(self):
        return hash(self.identifier)
