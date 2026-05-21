import asyncio

from pauperformance_bot.entity.config.creator import CreatorConfig
from pauperformance_bot.service.arena.twitch import TwitchService
from pauperformance_bot.service.arena.youtube import YouTubeService
from pauperformance_bot.service.mtg.scryfall import ScryfallService
from pauperformance_bot.service.nexus.async_discord_service import AsyncDiscordService
from pauperformance_bot.service.pauperformance.config_reader import ConfigReader
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
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
        warning_player: CreatorConfig = self.config_reader.get_pauperformance_creator()
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
        warning_player: CreatorConfig = self.config_reader.get_pauperformance_creator()
        videos = await asyncio.to_thread(
            self.youtube.get_channel_videos,
            player.youtube_channel_id,
        )
        await self.archive.archive_player_videos_from_youtube(
            player,
            videos,
            self.storage,
            self.discord,
            warning_player=warning_player,
            send_notification=send_notification,
        )
        logger.info(f"Processed videos from YouTube user {player.youtube_channel_id}.")
