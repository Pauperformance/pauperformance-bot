from typing import Optional

from pauperformance_bot.entity.api.archetype.archetype_card import ArchetypeCard
from pauperformance_bot.entity.api.archetype.discord_resource import DiscordResource
from pauperformance_bot.entity.api.archetype.resource import Resource
from pauperformance_bot.entity.api.archetype.sideboard_resource import SideboardResource
from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class Archetype:
    def __init__(
        self,
        *,
        name: str,
        aliases: Optional[list[str]],
        family: Optional[str],
        dominant_mana: list[str],
        game_type: list[str],
        description: str,
        staples: list[ArchetypeCard],
        frequent: list[ArchetypeCard],
        resource_sideboard: Optional[SideboardResource],
        resource_discord: Optional[DiscordResource],
        resources: list[Resource],
    ):
        self.name: str = name
        self.aliases: Optional[list[str]] = aliases
        self.family: Optional[str] = family
        self.dominant_mana: list[str] = dominant_mana
        self.game_type: list[str] = game_type
        self.description: str = description
        self.staples: list[ArchetypeCard] = staples
        self.frequent: list[ArchetypeCard] = frequent
        self.resource_sideboard: Optional[SideboardResource] = resource_sideboard
        self.resource_discord: Optional[DiscordResource] = resource_discord
        self.resources: list[Resource] = resources

    def __hash__(self):
        return hash(self.name)
