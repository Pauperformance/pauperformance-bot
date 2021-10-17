import time
from logging import INFO

from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard
from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.mtg.archive.local import LocalArchiveService
from pauperformance_bot.service.mtg.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.scryfall import ScryfallService
from pauperformance_bot.service.storage.dropbox_ import DropboxService
from pauperformance_bot.service.storage.local import LocalStorageService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()
logger.setLevel(INFO)


def _print_block(string):
    print(string, end="\n-------\n")


def demo_logger():
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    time.sleep(0.2)
    _print_block("")


def _get_playable_deck():
    mainboard = [PlayedCard(4, "Island"), PlayedCard(4, "Gush")]
    sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    return PlayableDeck(mainboard, sideboard)


def demo_entities():
    _print_block(_get_playable_deck())
    # other entities are harder to manually build: services will do it for us


def _demo_scryfall():
    scryfall = ScryfallService()

    rancor = scryfall.get_card_named("Rancor")
    _print_block(rancor)

    banned_cards = scryfall.get_banned_cards()
    for banned_card in banned_cards:
        print(f"{banned_card['name']}")
    _print_block("")

    deck = _get_playable_deck()
    _print_block(f"Legal: {deck.is_legal([c['name'] for c in banned_cards])}")

    results = scryfall.search_cards(
        "(oracle:deals oracle:damage oracle:draw) type:instant legal:pauper"
    )
    for result in results:
        print(f"{result['name']}")
    _print_block(f"[Found {len(results)} cards]")


def _get_local_pauperformance():
    storage = LocalStorageService()
    archive = LocalArchiveService()
    return PauperformanceService(storage, archive)


def _get_online_pauperformance():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    return PauperformanceService(storage, archive)


def _demo_academy():
    pauperformance = _get_local_pauperformance()
    # pauperformance = _get_online_pauperformance()  # requires Dropbox creds
    academy = AcademyService(pauperformance)
    academy.update_dev()
    # academy.update_archetypes()


def _demo_pauperformance():
    # pauperformance = _get_local_pauperformance()
    pauperformance = _get_online_pauperformance()  # requires Dropbox creds
    # _print_block(pauperformance.get_current_set_index())

    for deck in pauperformance.list_deckstats_decks():
        print(deck)
    _print_block("")

    for deck in pauperformance.list_archived_decks():
        print(deck)
    _print_block("")

    pauperformance.import_decks_from_deckstats()


def demo_services():
    _demo_scryfall()
    _demo_pauperformance()
    _demo_academy()


def update_dev(pauperformance):
    academy = AcademyService(pauperformance)
    academy.update_dev()


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


# def fz():
#     archived_decks = pauperformance.list_archived_decks()
#     for deck in archived_decks:
#         print(deck)
#     deckstats_deck = pauperformance.list_deckstats_decks()
#     for deck in deckstats_deck:
#         print(deck)
#     pauperformance.import_decks_from_deckstats(send_notification=False)
#     storage_names = storage.list_imported_deckstats_deck_names()
#     print(len(storage_names))
#     archive_names = [deck.name for deck in archive.list_decks()]
#     print(len(archive_names))
# print(set(storage_names) - set(archive_names))

# academy_update(pauperformance)


def main():
    demo_logger()
    demo_entities()
    demo_services()


if __name__ == "__main__":
    main()
