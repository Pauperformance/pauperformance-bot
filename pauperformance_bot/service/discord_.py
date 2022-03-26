import discord

from pauperformance_bot.constant.discord import (
    MAX_HISTORY_LIMIT,
    MYR_REACTION_KO,
    MYR_REACTION_OK,
    MYR_REACTION_SEEN,
    MYR_REACTION_WARNING,
)
from pauperformance_bot.constant.mtggoldfish import DECK_API_ENDPOINT
from pauperformance_bot.constant.players import PAUPERFORMANCE_PLAYERS
from pauperformance_bot.credentials import (
    DISCORD_BOT_TOKEN,
    DISCORD_CHANNEL_IMPORT_DECK_ID,
    DISCORD_CHANNEL_MYR_LOG_ID,
    DISCORD_CHANNEL_WELCOME_ID,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class DiscordService(discord.Client):
    def __init__(
        self,
        pauperformance,
        myr_bot_token=DISCORD_BOT_TOKEN,
        import_deck_channel_id=DISCORD_CHANNEL_IMPORT_DECK_ID,
        welcome_channel_id=DISCORD_CHANNEL_WELCOME_ID,
        myr_log_channel_id=DISCORD_CHANNEL_MYR_LOG_ID,
        **options,
    ):
        super().__init__(**options)
        self.pauperformance: PauperformanceService = pauperformance
        self.myr_bot_token = myr_bot_token
        self.import_deck_channel_id = import_deck_channel_id
        self.welcome_channel_id = welcome_channel_id
        self.myr_log_channel_id = myr_log_channel_id

    def import_decks(self):
        logger.info(f"Logging on Discord as {self.user}...")
        self.run(self.myr_bot_token)  # will automatically on_ready() on login

    async def on_ready(self):
        logger.info(f"Logged on Discord as {self.user}.")
        # await self.report_new_users()
        await self._import_new_decks()
        # await self._clean_emoji()
        # await self.list_channels_in_guild()
        self.loop.stop()

    # async def report_new_users(self):
    #     logger.info(f'Reporting new users from channel
    #     {self.welcome_channel_id}...')
    #     channel = self.get_channel(self.welcome_channel_id)
    #     print(channel.members)
    #     messages = await channel.history(limit=MAX_HISTORY_LIMIT).flatten()
    #     for m in messages:
    #         print(m.content)
    #         if m.author.name == 'MEE6' and m.content.startswith('Hey <@'):
    #             new_user_id = int(m.content[
    #                               m.content.index('@') + 1:
    #                               m.content.index('>')
    #                               ])
    #
    #             # print(f"New user: {new_user_id}")
    #             user = self.get_user(new_user_id)
    #             if user:
    #                 print(f"{user.display_name} ({new_user_id})")
    #     logger.info(
    #     f'Reported new users from channel {self.welcome_channel_id}.')

    async def _clean_emoji(self):
        channel = self.get_channel(self.import_deck_channel_id)
        messages = await channel.history(limit=MAX_HISTORY_LIMIT).flatten()
        for message in messages:
            await message.remove_reaction(MYR_REACTION_SEEN, self.user)
            await message.remove_reaction(MYR_REACTION_OK, self.user)
            await message.remove_reaction(MYR_REACTION_KO, self.user)
            await message.remove_reaction(MYR_REACTION_WARNING, self.user)

    async def _import_new_decks(self):
        logger.info(
            f"Importing new decks from channel "
            f"{self.import_deck_channel_id}..."
        )
        import_deck_channel = self.get_channel(self.import_deck_channel_id)
        myr_log_channel = self.get_channel(self.myr_log_channel_id)
        messages = await import_deck_channel.history(
            limit=MAX_HISTORY_LIMIT
        ).flatten()
        for message in messages:
            await self._process_import_deck_message(message, myr_log_channel)
        logger.info(
            f"Imported new decks from channel {self.import_deck_channel_id}."
        )

    async def _process_import_deck_message(self, message, log_channel):
        logger.debug(
            f"Processing message {message.id} by {message.author.id} "
            f"({message.author.name})..."
        )
        logger.info(f"Discord message {message.id}: {message.content}")
        await message.add_reaction(MYR_REACTION_SEEN)
        if message.content.strip().startswith(DECK_API_ENDPOINT):
            logger.info("Detected MTGGoldfish deck.")
            await self._try_import_mtggoldfish_deck(message, log_channel)
        else:
            logger.info("Unrecognized deck format. Skipping it.")
            await message.remove_reaction(MYR_REACTION_SEEN, self.user)
            await message.add_reaction(MYR_REACTION_KO)
        logger.debug(
            f"Processed message {message.id} by {message.author.id} "
            f"({message.author.name})."
        )

    async def _try_import_mtggoldfish_deck(self, message, log_channel):
        url = message.content.strip()
        if "#" in url:
            url = url[: url.index("#")]
        logger.debug(f"Polished URL: {url}")
        candidates = [
            p
            for p in PAUPERFORMANCE_PLAYERS
            if p.discord_id == message.author.id
        ]
        if len(candidates) != 1:
            log_message = (
                f"Unable to unambiguously determine deck owner "
                f"for <{url}>. Candidates are: {candidates}."
            )
            logger.warning(log_message)
            await log_channel.send(log_message)
            await message.remove_reaction(MYR_REACTION_SEEN, self.user)
            await message.add_reaction(MYR_REACTION_KO)
            return
        player = candidates[0]
        logger.debug(f"Detected owner: {player.name}")

        await self.pauperformance.archive.import_player_deck_from_mtggoldfish(
            url,
            player,
            self,
            message,
            log_channel,
            None,
            send_notification=True,
        )
