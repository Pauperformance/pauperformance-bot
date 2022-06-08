from pauperformance_bot.constant.discord import (
    DISCORD_MAX_HISTORY_LIMIT,
    DISCORD_MYR_REACTION_KO,
    DISCORD_MYR_REACTION_SEEN,
)
from pauperformance_bot.constant.mtggoldfish import DECK_API_ENDPOINT
from pauperformance_bot.entity.config.phd import PhDConfig
from pauperformance_bot.service.config_reader import ConfigReader
from pauperformance_bot.service.nexus.async_discord_service import AsyncDiscordService
from pauperformance_bot.service.nexus.sync.messages_sender import (
    DiscordMessagesSenderSyncService,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.scryfall import ScryfallService
from pauperformance_bot.service.twitch import TwitchService
from pauperformance_bot.service.youtube import YouTubeService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class AsyncPauperformanceService(PauperformanceService):
    def __init__(
        self,
        discord,
        storage,
        archive,
        scryfall=ScryfallService(),
        twitch=TwitchService(),
        youtube=YouTubeService(),
        config_reader=ConfigReader(),
    ):
        super().__init__(
            storage,
            archive,
            scryfall,
            twitch,
            youtube,
            config_reader,
        )
        self.discord: AsyncDiscordService = discord

    async def import_decks_from_deckstats(self, send_notification=True):
        logger.info("Updating Archive decks for all users...")
        players_by_deckstats_id = {
            int(p.deckstats_id): p for p in self.players if p.deckstats_id
        }
        warning_player: PhDConfig = self.config_reader.get_pauperformance_phd()
        for player in self.players:
            if not player.deckstats_id:
                logger.info(
                    f"Skipping player {player.name} with no Deckstats account..."
                )
                continue

            await self.archive.import_player_decks_from_deckstats(
                player,
                self.storage,
                players_by_deckstats_id,
                self.set_index,
                self.discord,
                warning_player=warning_player,
                send_notification=send_notification,
            )
        logger.info("Updated Archive decks for all users.")

    async def import_players_videos_from_twitch(self, send_notification=True):
        logger.info("Updating Twitch videos for all users...")
        for player in self.players:
            if not player.twitch_login_name:
                logger.info(f"Skipping player {player.name} with no Twitch account...")
                continue

            await self.import_player_videos_from_twitch(
                player,
                send_notification=send_notification,
            )
        logger.info("Updated Twitch videos for all users.")

    async def import_player_videos_from_twitch(self, player, send_notification=True):
        logger.info(f"Processing videos from Twitch user {player.twitch_login_name}...")
        twitch_user = self.twitch.get_user(player.twitch_login_name)
        warning_player: PhDConfig = self.config_reader.get_pauperformance_phd()
        await self.archive.archive_player_videos_from_twitch(
            player,
            self.twitch.get_user_videos(twitch_user.user_id),
            self.storage,
            self.discord,
            warning_player=warning_player,
            send_notification=send_notification,
        )
        logger.info(f"Processed videos from Twitch user {player.twitch_login_name}.")

    async def import_players_videos_from_youtube(self, send_notification=True):
        logger.info("Updating YouTube videos for all users...")
        for player in self.players:
            if not player.youtube_channel_id:
                logger.info(f"Skipping player {player.name} with no YouTube account...")
                continue

            await self.import_player_videos_from_youtube(
                player,
                send_notification=send_notification,
            )
        logger.info("Updated YouTube videos for all users.")

    async def import_player_videos_from_youtube(self, player, send_notification=True):
        logger.info(
            f"Processing videos from YouTube user " f"{player.youtube_channel_id}..."
        )
        warning_player: PhDConfig = self.config_reader.get_pauperformance_phd()
        await self.archive.archive_player_videos_from_youtube(
            player,
            self.youtube.get_channel_videos(
                player.youtube_channel_id,
                player.default_youtube_language,
            ),
            self.storage,
            self.discord,
            warning_player=warning_player,
            send_notification=send_notification,
        )
        logger.info(f"Processed videos from YouTube user {player.youtube_channel_id}.")

    async def import_decks_from_discord(self, send_notification=True):
        import_deck_channel_id = self.discord.import_deck_channel_id
        logger.info(f"Importing new decks from channel {import_deck_channel_id}...")
        import_deck_channel = self.discord.get_channel(import_deck_channel_id)
        messages = await import_deck_channel.history(
            limit=DISCORD_MAX_HISTORY_LIMIT
        ).flatten()
        for message in messages:
            await self._process_discord_import_deck_message(message, send_notification)
        logger.info(f"Imported new decks from channel {import_deck_channel_id}.")

    async def _process_discord_import_deck_message(self, message, send_notification):
        logger.debug(
            f"Processing message {message.id} by {message.author.id} "
            f"({message.author.name})..."
        )
        logger.info(f"Discord message {message.id}: {message.content}")
        await message.add_reaction(DISCORD_MYR_REACTION_SEEN)
        if message.content.strip().startswith(DECK_API_ENDPOINT):
            logger.info("Detected MTGGoldfish deck.")
            await self._try_import_mtggoldfish_deck_from_discord(
                message, send_notification
            )
        else:
            log_message = (
                f"Unrecognized deck format in message {message.content}. Skipping it."
            )
            logger.info(log_message)
            discord_logger = DiscordMessagesSenderSyncService([log_message])
            discord_logger.run_task()
            await message.remove_reaction(DISCORD_MYR_REACTION_SEEN, self.discord.user)
            await message.add_reaction(DISCORD_MYR_REACTION_KO)
        logger.debug(
            f"Processed message {message.id} by {message.author.id} "
            f"({message.author.name})."
        )

    async def _try_import_mtggoldfish_deck_from_discord(
        self, message, send_notification
    ):
        url = message.content.strip()
        if "#" in url:
            url = url[: url.index("#")]
        logger.debug(f"Polished URL: {url}")
        candidates = [p for p in self.players if p.discord_id == message.author.id]
        player = candidates[-1]
        logger.debug(f"Detected owner: {player.name}")
        await self.archive.import_player_deck_from_mtggoldfish(
            url,
            player,
            self,
            message,
            None,
            send_notification=send_notification,
        )
