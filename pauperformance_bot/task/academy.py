from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.discord_ import DiscordService
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.dropbox_ import DropboxService


def academy_update(pauperformance):
    # import new content
    pauperformance.import_players_videos_from_twitch(send_notification=True)
    pauperformance.import_players_videos_from_youtube(send_notification=True)
    pauperformance.import_decks_from_deckstats(send_notification=True)

    # update pages
    academy = AcademyService(pauperformance)
    academy.update_all(update_dev=False)  # avoid unnecessary changes


def main():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)
    discord = DiscordService(pauperformance)
    discord.import_decks()
    academy_update(pauperformance)


if __name__ == "__main__":
    main()
