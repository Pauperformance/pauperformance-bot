import asyncio

from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.nexus.async_discord_service import AsyncDiscordService
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.async_pauperformance import (
    AsyncPauperformanceService,
)
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService


async def async_setup_pauperformance_service():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    discord = AsyncDiscordService()
    pauperformance = AsyncPauperformanceService(discord, storage, archive)
    await pauperformance.discord.wait_until_ready()
    return pauperformance


async def async_import_players_videos_from_twitch(send_notification=True, update_dev=True):
    pauperformance = await async_setup_pauperformance_service()
    await pauperformance.import_players_videos_from_twitch(send_notification)
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev)


async def async_import_players_videos_from_youtube(send_notification=True, update_dev=True):
    pauperformance = await async_setup_pauperformance_service()
    await pauperformance.import_players_videos_from_youtube(send_notification)
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev)


async def async_import_decks_from_deckstats(send_notification=True, update_dev=True):
    pauperformance = await async_setup_pauperformance_service()
    await pauperformance.import_decks_from_deckstats(send_notification)
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev)


async def async_import_decks_from_discord(send_notification=True, update_dev=True):
    pauperformance = await async_setup_pauperformance_service()
    await pauperformance.import_decks_from_discord(send_notification)
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev)


async def async_academy_update():
    pauperformance = await async_setup_pauperformance_service()

    # import new content
    await pauperformance.import_players_videos_from_twitch(send_notification=True)
    await pauperformance.import_players_videos_from_youtube(send_notification=True)
    await pauperformance.import_decks_from_deckstats(send_notification=True)
    await pauperformance.import_decks_from_discord(send_notification=True)

    # update pages
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev=False)  # avoid unnecessary changes


def run_coroutine_in_event_loop(coroutine, **kwargs):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(coroutine(**kwargs))
    finally:
        loop.close()


def main():
    run_coroutine_in_event_loop(async_academy_update)


if __name__ == "__main__":
    main()
