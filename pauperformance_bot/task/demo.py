from pauperformance_bot.service.academy import Academy
from pauperformance_bot.service.mtg.archive.local import Local as LocalArchive
from pauperformance_bot.service.pauperformance import Pauperformance
from pauperformance_bot.service.storage.local import Local as LocalStorage


def update_dev(pauperformance):
    academy = Academy(pauperformance)
    academy.update_dev()


def main():
    storage = LocalStorage()
    archive = LocalArchive()
    pauperformance = Pauperformance(storage, archive)

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
