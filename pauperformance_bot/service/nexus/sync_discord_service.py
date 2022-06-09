import asyncio
from abc import ABC, abstractmethod

from pauperformance_bot.constant.pauperformance.nexus import (
    DISCORD_CHANNEL_IMPORT_DECK_ID,
    DISCORD_CHANNEL_MYR_LOG_ID,
    DISCORD_CHANNEL_WELCOME_ID,
)
from pauperformance_bot.credentials import DISCORD_BOT_TOKEN
from pauperformance_bot.service.nexus.abstract_discord_service import (
    AbstractDiscordService,
)
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class AbstractSyncDiscordService(AbstractDiscordService, ABC):
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
        self.result = None

    def run_task(self):
        logger.info("Logging on Discord with token...")
        self.run(self.myr_bot_token)  # will call on_ready()

    async def on_ready(self):
        logger.info(f"Logged on Discord as {self.user}.")
        logger.info(f"Retrieving log channel (id: {self.myr_log_channel_id})...")
        self.log_channel = self.get_channel(self.myr_log_channel_id)
        logger.info("Retrieved log channel.")
        self.result = await self._task()
        self.loop.stop()
        # create a new event loop for possible future SyncDiscordServices
        asyncio.set_event_loop(asyncio.new_event_loop())

    @abstractmethod
    async def _task(self):
        pass

    @property
    def log_channel(self):
        return self._log_channel

    @log_channel.setter
    def log_channel(self, value):
        self._log_channel = value
