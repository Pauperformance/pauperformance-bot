from typing import Optional

from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class SideboardResource:
    def __init__(
        self,
        *,
        link: str,
    ):
        self.link: str = link

    def __hash__(self):
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
    ):
        self.name: str = name
        self.link: str = link
        self.language: str = language

    def __hash__(self):
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
    ):
        self.name: str = name
        self.link: str = link
        self.language: str = language
        self.author: str = author
        self.date: str = date

    def __hash__(self):
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
        link: Optional[str],
    ):
        self.text: str = text
        self.date: str = date
        self.scope: str = scope
        self.link: Optional[str] = link

    def __hash__(self):
        return hash(self.text)


@auto_repr
@auto_str
class ArchetypeConfig:
    def __init__(
        self,
        *,
        name: str,
        aliases: list[str],
        family: Optional[str],
        dominant_mana: list[str],
        game_type: list[str],
        description: str,
        must_have_cards: list[str],
        must_not_have_cards: list[str],
        reference_decks: list[str],
        resource_sideboard: Optional[SideboardResource],
        resources_discord: list[DiscordResource],
        resources: list[Resource],
    ):
        self.name: str = name
        self.aliases: list[str] = aliases
        self.family: Optional[str] = family
        self.dominant_mana: list[str] = dominant_mana
        self.game_type: list[str] = game_type
        self.description: str = description
        self.must_have_cards: list[str] = must_have_cards
        self.must_not_have_cards: list[str] = must_not_have_cards
        self.reference_decks: list[str] = reference_decks
        self.resource_sideboard: Optional[SideboardResource] = resource_sideboard
        self.resources_discord: list[DiscordResource] = resources_discord
        self.resources: list[Resource] = resources

    def __hash__(self):
        return hash(self.name)
