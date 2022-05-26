from pauperformance_bot.entity.api.archetype import Resource
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
