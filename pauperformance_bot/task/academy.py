import asyncio

from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.archive.mtggoldfish import MTGGoldfishArchiveService
from pauperformance_bot.service.async_pauperformance import AsyncPauperformanceService
from pauperformance_bot.service.discord_.async_discord_service import (
    AsyncDiscordService,
)
from pauperformance_bot.service.storage.dropbox_ import DropboxService


async def async_academy_update():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    discord = AsyncDiscordService()
    pauperformance = AsyncPauperformanceService(discord, storage, archive)
    await pauperformance.discord.wait_until_ready()

    # import new content
    await pauperformance.import_players_videos_from_twitch(send_notification=True)
    await pauperformance.import_players_videos_from_youtube(send_notification=True)
    await pauperformance.import_decks_from_deckstats(send_notification=True)
    await pauperformance.import_decks_from_discord(send_notification=True)

    # update pages
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev=False)  # avoid unnecessary changes


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_academy_update())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
