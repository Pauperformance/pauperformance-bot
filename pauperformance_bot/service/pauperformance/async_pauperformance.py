import asyncio

from pauperformance_bot.constant.arena.youtube import YOUTUBE_CONNECTION_POOL_SIZE_API
from pauperformance_bot.entity.config.creator import CreatorConfig
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
        youtube=YouTubeService(),
        config_reader=ConfigReader(),
    ):
        super().__init__(
            storage,
            archive,
            scryfall,
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

    async def import_players_videos_from_youtube(self, since=None):
        logger.info("Updating YouTube videos for all users...")
        imported_youtube_videos = await asyncio.to_thread(
            self.storage.list_imported_youtube_videos_ids
        )
        players_with_youtube = [p for p in self.players if p.youtube_channel_id]
        semaphore = asyncio.Semaphore(YOUTUBE_CONNECTION_POOL_SIZE_API)

        async def bounded(player):
            async with semaphore:
                await self.import_player_videos_from_youtube(
                    player, imported_youtube_videos, since=since
                )

        await asyncio.gather(*(bounded(player) for player in players_with_youtube))
        logger.info("Updated YouTube videos for all users.")

    async def import_player_videos_from_youtube(
        self, player, imported_youtube_videos: set, since=None
    ):
        logger.info(
            f"Processing videos from YouTube user {player.youtube_channel_id}..."
        )
        videos = await asyncio.to_thread(
            self.youtube.get_channel_videos,
            player.youtube_channel_id,
            since,
        )
        await asyncio.to_thread(
            self.archive.archive_player_videos_from_youtube,
            player,
            videos,
            self.storage,
            imported_youtube_videos,
        )
        logger.info(f"Processed videos from YouTube user {player.youtube_channel_id}.")
