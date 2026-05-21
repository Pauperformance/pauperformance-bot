import asyncio

from tenacity import (
    retry,
    retry_if_exception_message,
    stop_after_attempt,
    wait_random_exponential,
)

from pauperformance_bot.service.nexus.async_discord_service import AsyncDiscordService
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.async_pauperformance import (
    AsyncPauperformanceService,
)
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


@retry(
    retry=retry_if_exception_message(match=r".*Event loop is closed.*"),
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=1, max=60),
)
async def async_academy_update():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    discord = AsyncDiscordService()
    pauperformance = AsyncPauperformanceService(discord, storage, archive)
    await pauperformance.discord.wait_until_ready()

    try:
        # import new content
        send_notification = False
        await pauperformance.import_players_videos_from_youtube(
            send_notification=send_notification
        )
        # await pauperformance.import_decks_from_deckstats(
        #     send_notification=send_notification
        # )

        # update pages
        # academy = AcademyService(pauperformance)
        # academy.update_all()
    finally:
        await pauperformance.discord.close()


@retry(
    retry=retry_if_exception_message(
        match=r".*Server Error.*|" r".*Internal error encountered.*|"
    ),
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=1, max=60),
)
def main():
    try:
        asyncio.run(async_academy_update())
    except RuntimeError as exc:
        logger.exception(exc)


if __name__ == "__main__":
    main()
