import asyncio

from pauperformance_bot.constant.discord import (
    DISCORD_CHANNEL_IMPORT_DECK_ID,
    DISCORD_CHANNEL_MYR_LOG_ID,
    DISCORD_CHANNEL_WELCOME_ID,
    DISCORD_MAX_HISTORY_LIMIT,
    DISCORD_MYR_REACTION_KO,
    DISCORD_MYR_REACTION_OK,
    DISCORD_MYR_REACTION_SEEN,
    DISCORD_MYR_REACTION_WARNING,
)
from pauperformance_bot.credentials import DISCORD_BOT_TOKEN
from pauperformance_bot.service.discord_.abstract_discord_service import (
    AbstractDiscordService,
)
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class AsyncDiscordService(AbstractDiscordService):
    def __init__(
        self,
        myr_bot_token=DISCORD_BOT_TOKEN,
        import_deck_channel_id=DISCORD_CHANNEL_IMPORT_DECK_ID,
        welcome_channel_id=DISCORD_CHANNEL_WELCOME_ID,
        myr_log_channel_id=DISCORD_CHANNEL_MYR_LOG_ID,
        **options,
    ):
        super().__init__(
            myr_bot_token=myr_bot_token,
            import_deck_channel_id=import_deck_channel_id,
            welcome_channel_id=welcome_channel_id,
            myr_log_channel_id=myr_log_channel_id,
            **options,
        )
        self._log_channel = None
        asyncio.create_task(self._run_background())  # fire and forget call

    async def _run_background(self):
        logger.info("AsyncDiscordService starting in background...")
        logger.info("Logging on Discord with token...")
        await self.start(self.myr_bot_token)  # will call on_ready()
        logger.info("AsyncDiscordService stopped in background.")

    async def wait_until_ready(self):
        await super().wait_until_ready()
        logger.info(
            f"Retrieving log channel (id: {self.myr_log_channel_id})..."
        )
        self.log_channel = self.get_channel(self.myr_log_channel_id)
        logger.info("Retrieved log channel.")

    async def on_ready(self):
        logger.info(f"Logged on Discord as {self.user}.")

    async def _clean_my_emoji(self, channel_id):
        channel = self.get_channel(channel_id)
        messages = await channel.history(
            limit=DISCORD_MAX_HISTORY_LIMIT
        ).flatten()
        for m in messages:
            await m.remove_reaction(DISCORD_MYR_REACTION_SEEN, self.user)
            await m.remove_reaction(DISCORD_MYR_REACTION_OK, self.user)
            await m.remove_reaction(DISCORD_MYR_REACTION_KO, self.user)
            await m.remove_reaction(DISCORD_MYR_REACTION_WARNING, self.user)

    @property
    def log_channel(self):
        return self._log_channel

    @log_channel.setter
    def log_channel(self, value):
        self._log_channel = value
