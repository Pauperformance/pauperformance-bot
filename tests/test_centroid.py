from statistics import mean, stdev, variance

from service.pauperformance.silver.deckstatistics import DeckstatisticsFactory

from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.academy.data_loader import AcademyDataLoader
from pauperformance_bot.service.pauperformance.archive.local import LocalArchiveService
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.storage.local import LocalStorageService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


def test_centroid():
    storage = LocalStorageService()
    archive = LocalArchiveService()
    pauperformance = PauperformanceService(storage, archive)
    academy = AcademyService(pauperformance)
    archetype = "Burn"
    # index = academy.set_index
    # logger.info(index)
    loader = AcademyDataLoader()
    am = DeckstatisticsFactory(academy, loader).build_metadata_for(archetype)
    logger.info(am.cards)
    logger.info(f"nr. decks: {am.nr_decks} max: {am.most_played_card}")
    dfq = am.deck_occurrences_ratio()
    cfq = am.card_playing_rate()
    logger.info("# DECKS")
    logger.info(f"max deck freq.: {dfq[0]}")
    centroid = sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.9, dfq))))
    logger.info(f"centroid(decks): {centroid}")
    deck_freqs = [f[1] for f in dfq]
    mean_deck_freq = mean(deck_freqs)
    logger.info(f"stdev: {stdev(deck_freqs)}  variance: {variance(deck_freqs)}")
    logger.info(f"mean {mean_deck_freq}")
    logger.info("# CARDS")
    logger.info(f"max card freq {cfq[0]}")
    centroid = sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.07, cfq))))
    logger.info(f"centroid(cards): {centroid}")
    card_freqs = [f[1] for f in cfq]
    mean_card_freq = mean(card_freqs)
    logger.info(f"stdev: {stdev(card_freqs)} variance: {variance(card_freqs)}")
    logger.info(f"mean {mean_card_freq}")
    s_card_fqs = sorted(
        list(
            map(
                lambda f: f[0],
                filter(lambda f: f[1] >= mean_card_freq + stdev(card_freqs), cfq),
            )
        )
    )
    logger.info(f"staples(cards): {s_card_fqs}")
    assert True
