import time
from logging import INFO

from pauperformance_bot.constant.players import SHIKA93_PLAYER
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard
from pauperformance_bot.service.academy import AcademyService
from pauperformance_bot.service.archive.local import LocalArchiveService
from pauperformance_bot.service.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.scryfall import ScryfallService
from pauperformance_bot.service.storage.dropbox_ import DropboxService
from pauperformance_bot.service.storage.local import LocalStorageService
from pauperformance_bot.service.telegram import TelegramService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()
logger.setLevel(INFO)


def demo_logger():
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    time.sleep(0.2)
    _print_block("")


def demo_entities():
    _print_block(_get_playable_deck())
    # other entities are harder to manually build: services will do it for us


def demo_services():
    _demo_scryfall()
    _demo_telegram()
    _demo_storage()
    _demo_archive()
    _demo_pauperformance()
    _demo_academy()


def _print_block(string):
    print(string, end="\n-------\n")


def _get_playable_deck():
    mainboard = [PlayedCard(4, "Island"), PlayedCard(4, "Gush")]
    sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    return PlayableDeck(mainboard, sideboard)


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


def _demo_storage():
    # storage = DropboxService()
    storage = LocalStorageService()
    for deck in storage.list_imported_deckstats_deck_names():
        print(deck)
    _print_block("")


def _demo_archive():
    # archive = LocalArchiveService()
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    for deck in archive.list_decks():
        print(deck)
    _print_block("")


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
    pauperformance = _get_local_pauperformance()
    # pauperformance = _get_online_pauperformance()
    _print_block(pauperformance.get_current_set_index())

    for deck in pauperformance.list_deckstats_decks():
        print(deck)
    _print_block("")

    pauperformance.import_decks_from_deckstats(send_notification=False)


def _demo_telegram():
    telegram = TelegramService()
    telegram.send_message(SHIKA93_PLAYER, "Live demo!")


def main():
    demo_logger()
    demo_entities()
    demo_services()


if __name__ == "__main__":
    main()
