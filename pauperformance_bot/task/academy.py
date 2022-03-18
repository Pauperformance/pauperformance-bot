from pauperformance_bot.service.academy import AcademyService

# from pauperformance_bot.service.archive.local import (
#     LocalArchiveService as LocalArchive,
# )
from pauperformance_bot.service.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.dropbox_ import DropboxService

# from pauperformance_bot.service.storage.local import (
#     LocalStorageService as LocalStorage,
# )


def academy_update(pauperformance):
    # import new content
    pauperformance.import_players_videos_from_twitch(send_notification=True)
    pauperformance.import_players_videos_from_youtube(send_notification=True)
    pauperformance.import_decks_from_deckstats(send_notification=True)
    # update Academy
    academy = AcademyService(pauperformance)
    academy.update_all()


def main():
    # storage = LocalStorage()
    storage = DropboxService()
    # archive = LocalArchive()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)
    academy_update(pauperformance)


if __name__ == "__main__":
    main()
