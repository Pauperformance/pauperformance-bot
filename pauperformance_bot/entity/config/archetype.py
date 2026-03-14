from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class SideboardResource:
    def __init__(
        self,
        *,
        link: str,
    ) -> None:
        self.link = link

    def __hash__(self) -> int:
        return hash(self.link)


@auto_repr
@auto_str
class DiscordResource:
    def __init__(
        self,
        *,
        name: str,
        link: str,
        language: str,
    ) -> None:
        self.name = name
        self.link = link
        self.language = language

    def __hash__(self) -> int:
        return hash(self.link)


@auto_repr
@auto_str
class Resource:
    def __init__(
        self,
        *,
        name: str,
        link: str,
        language: str,
        author: str,
        date: str,
    ) -> None:
        self.name = name
        self.link = link
        self.language = language
        self.author = author
        self.date = date

    def __hash__(self) -> int:
        return hash(self.link)


@auto_repr
@auto_str
class ChangelogEntry:
    def __init__(
        self,
        *,
        text: str,
        date: str,
        scope: str,
        link: str | None,
    ) -> None:
        self.text = text
        self.date = date
        self.scope = scope
        self.link = link

    def __hash__(self) -> int:
        return hash(self.text)


@auto_repr
@auto_str
class ArchetypeConfig:
    def __init__(
        self,
        *,
        name: str,
        aliases: list[str],
        family: str | None,
        dominant_mana: list[str],
        game_type: list[str],
        description: str,
        must_have_cards: list[str],
        must_not_have_cards: list[str],
        reference_decks: list[str],
        resource_sideboard: SideboardResource | None,
        resources_discord: list[DiscordResource],
        resources: list[Resource],
    ) -> None:
        self.name = name
        self.aliases = aliases
        self.family = family
        self.dominant_mana = dominant_mana
        self.game_type = game_type
        self.description = description
        self.must_have_cards = must_have_cards
        self.must_not_have_cards = must_not_have_cards
        self.reference_decks = reference_decks
        self.resource_sideboard = resource_sideboard
        self.resources_discord = resources_discord
        self.resources = resources

    def __hash__(self) -> int:
        return hash(self.name)
