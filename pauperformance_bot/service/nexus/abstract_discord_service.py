from abc import ABC, abstractmethod
from typing import Any

import discord

from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class AbstractDiscordService(discord.Client, ABC):  # type: ignore[misc]
    def __init__(
        self,
        myr_bot_token: str | None,
        import_deck_channel_id: int,
        welcome_channel_id: int,
        myr_log_channel_id: int,
        **options: Any,
    ) -> None:
        super().__init__(**options)
        self.myr_bot_token = myr_bot_token
        self.import_deck_channel_id = import_deck_channel_id
        self.welcome_channel_id = welcome_channel_id
        self.myr_log_channel_id = myr_log_channel_id

    @property
    @abstractmethod
    def log_channel(self) -> discord.TextChannel | None:
        pass

    async def send_log_message(self, message: str) -> None:
        await self.log_channel.send(message)  # type: ignore[union-attr]

    async def send_user_message(self, user_id: int, message: str) -> None:
        user = await self.fetch_user(user_id)
        await user.send(message)

    def list_roles(self, guild_id: int) -> list[discord.Role]:
        return self.get_guild(guild_id).roles  # type: ignore[no-any-return]
