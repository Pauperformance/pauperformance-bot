from typing import Optional

from pauperformance_bot.entity.config.archetype import (
    ArchetypeConfig,
    DiscordResource,
    Resource,
    SideboardResource,
)
from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class ArchetypeCard:
    def __init__(
        self,
        *,
        name: str,
        link: str,
        preview: str,
    ):
        self.name: str = name
        self.link: str = link
        self.preview: str = preview

    def __hash__(self):
        return hash(self.name)


@auto_repr
@auto_str
class Archetype(ArchetypeConfig):
    def __init__(
        self,
        *,
        name: str,
        aliases: Optional[list[str]],
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
        staples: list[ArchetypeCard],
        frequent: list[ArchetypeCard],
    ):
        super().__init__(
            name=name,
            aliases=aliases,
            family=family,
            dominant_mana=dominant_mana,
            game_type=game_type,
            description=description,
            must_have_cards=must_have_cards,
            must_not_have_cards=must_not_have_cards,
            reference_decks=reference_decks,
            resource_sideboard=resource_sideboard,
            resources_discord=resources_discord,
            resources=resources,
        )
        self.staples: list[ArchetypeCard] = staples
        self.frequent: list[ArchetypeCard] = frequent

    def __hash__(self):
        return hash(self.name)
