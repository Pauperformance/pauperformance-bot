from abc import ABC, abstractmethod

import discord

from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class AbstractDiscordService(discord.Client, ABC):
    def __init__(
        self,
        myr_bot_token,
        import_deck_channel_id,
        welcome_channel_id,
        myr_log_channel_id,
        **options,
    ):
        super().__init__(**options)
        self.myr_bot_token = myr_bot_token
        self.import_deck_channel_id = import_deck_channel_id
        self.welcome_channel_id = welcome_channel_id
        self.myr_log_channel_id = myr_log_channel_id

    @property
    @abstractmethod
    def log_channel(self):
        pass

    async def send_log_message(self, message):
        await self.log_channel.send(message)

    async def send_user_message(self, user_id, message):
        user = await self.fetch_user(user_id)
        await user.send(message)
