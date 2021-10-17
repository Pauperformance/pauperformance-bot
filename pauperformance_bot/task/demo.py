from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard
from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.mtg.archive.local import (
    LocalArchiveService as LocalArchive,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.local import (
    LocalStorageService as LocalStorage,
)


def update_dev(pauperformance):
    academy = AcademyService(pauperformance)
    academy.update_dev()


def make_playable_deck():
    mainboard = [PlayedCard(4, "Island"), PlayedCard(4, "Swamp")]
    sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    return PlayableDeck(mainboard, sideboard)


# def foo():
#     myr = MyrService()
#     myr.send_message(SHIKA93_PLAYER, "📌 Test.")

# storage = DropboxService()
# mtgg = MTGGoldfishArchiveService(storage)
# decks = mtgg.list_decks()
# print(decks)
#
#     deck = PlayableDeck(main, sideboard)
#     # print(deck)
#     archive = LocalArchiveService()
#     # new_deck = archive.create_deck(
#     #     "Acid Trip 576.001.AzoriusFlavoredGamerGirlPee | "
#     #     "Ravnica Allegiance (rna)",
#     #     "My description",
#     #     deck,
#     # )
#     # print(new_deck)
#     decks = archive.list_decks()
#     deck = archive.to_playable_deck(decks[0])
#     print(deck)

#
# storage = LocalStorageService()
# key = storage.get_imported_deckstats_deck_key(
#     "2059767",
#     "4351760",
#     "Aristocrats 676.001.MrEvilEye | Modern Horizons 2 (mh2)",
# )
# print(key)
# main = [PlayedCard(4, "Island"), PlayedCard(4, "Swamp")]
# sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
# deck = PlayableDeck(main, sideboard)
# # storage.create_file(key, str(deck))
# print(storage.list_imported_deckstats_deck_ids())
# print(storage.list_imported_deckstats_deck_names())


def main():
    storage = LocalStorage()
    archive = LocalArchive()
    pauperformance = PauperformanceService(storage, archive)

    archived_decks = pauperformance.list_archived_decks()
    for deck in archived_decks:
        print(deck)
    deckstats_deck = pauperformance.list_deckstats_decks()
    for deck in deckstats_deck:
        print(deck)
    pauperformance.import_decks_from_deckstats(send_notification=False)
    storage_names = storage.list_imported_deckstats_deck_names()
    print(len(storage_names))
    archive_names = [deck.name for deck in archive.list_decks()]
    print(len(archive_names))
    # print(set(storage_names) - set(archive_names))

    # academy_update(pauperformance)


if __name__ == "__main__":
    main()
