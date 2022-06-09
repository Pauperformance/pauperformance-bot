from pauperformance_bot.constant.pauperformance.nexus import (
    DISCORD_CHANNEL_IMPORT_DECK_ID,
    DISCORD_CHANNEL_MYR_LOG_ID,
    DISCORD_CHANNEL_WELCOME_ID,
    DISCORD_MAX_HISTORY_LIMIT,
)
from pauperformance_bot.credentials import DISCORD_BOT_TOKEN
from pauperformance_bot.service.nexus.sync_discord_service import (
    AbstractSyncDiscordService,
)
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DiscordMembersFetcherSyncService(AbstractSyncDiscordService):
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
        self.result = {}

    async def _task(self):
        return await self._fetch_members()

    async def _fetch_members(self):
        welcome_channel = self.get_channel(self.welcome_channel_id)
        messages = await welcome_channel.history(
            limit=DISCORD_MAX_HISTORY_LIMIT
        ).flatten()
        users = {}
        for message in messages:
            users[message.author.display_name] = message.author.id
        logger.info(f"Discord users: {users}")
        return users
