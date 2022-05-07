from pauperformance_bot.constant.discord import (
    DISCORD_CHANNEL_IMPORT_DECK_ID,
    DISCORD_CHANNEL_MYR_LOG_ID,
    DISCORD_CHANNEL_WELCOME_ID,
)
from pauperformance_bot.credentials import DISCORD_BOT_TOKEN
from pauperformance_bot.service.discord_.sync_discord_service import (
    AbstractSyncDiscordService,
)
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DiscordMessagesSenderSyncService(AbstractSyncDiscordService):
    def __init__(
        self,
        messages,
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
        self.messages = messages
        self.result = False

    async def _task(self):
        for message in self.messages:
            await self.send_log_message(message)
        return True
