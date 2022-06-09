from pauperformance_bot.entity.api.archetype import Resource
from pauperformance_bot.entity.config.archetype import ChangelogEntry
from pauperformance_bot.util.entities import auto_repr, auto_str


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
