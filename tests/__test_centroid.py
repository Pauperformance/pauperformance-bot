import logging
from statistics import mean, stdev, variance

from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.academy.data_loader import AcademyDataLoader
from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.deckstatistics import (
    DeckstatisticsFactory,
)
from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService
from pauperformance_bot.util.log import get_application_logger

logger: logging.Logger = get_application_logger()


def test_centroid() -> None:
    storage: DropboxService = DropboxService()
    archive: MTGGoldfishArchiveService = MTGGoldfishArchiveService(storage)
    pauperformance: PauperformanceService = PauperformanceService(storage, archive)
    academy: AcademyService = AcademyService(pauperformance)
    archetype: str = "Burn"
    loader: AcademyDataLoader = AcademyDataLoader()
    am = DeckstatisticsFactory(academy.scryfall, loader).build_metadata_for(archetype)
    logger.info(am.cards)
    logger.info(f"nr. decks: {am.nr_decks} max: {am.most_played_card}")
    dfq: list[tuple[str, float]] = am.deck_occurrences_ratio()
    cfq: list[tuple[str, float]] = am.card_playing_rate()
    logger.info("# DECKS")
    logger.info(f"max deck freq.: {dfq[0]}")
    centroid: list[str] = sorted(
        list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.9, dfq)))
    )
    logger.info(f"centroid(decks): {centroid}")
    deck_freqs: list[float] = [f[1] for f in dfq]
    mean_deck_freq: float = mean(deck_freqs)
    logger.info(f"stdev: {stdev(deck_freqs)}  variance: {variance(deck_freqs)}")
    logger.info(f"mean {mean_deck_freq}")
    logger.info("# CARDS")
    logger.info(f"max card freq {cfq[0]}")
    centroid = sorted(list(map(lambda f: f[0], filter(lambda f: f[1] >= 0.07, cfq))))
    logger.info(f"centroid(cards): {centroid}")
    card_freqs: list[float] = [f[1] for f in cfq]
    mean_card_freq: float = mean(card_freqs)
    logger.info(f"stdev: {stdev(card_freqs)} variance: {variance(card_freqs)}")
    logger.info(f"mean {mean_card_freq}")
    s_card_fqs: list[str] = sorted(
        list(
            map(
                lambda f: f[0],
                filter(lambda f: f[1] >= mean_card_freq + stdev(card_freqs), cfq),
            )
        )
    )
    logger.info(f"staples(cards): {s_card_fqs}")
    assert "Mountain" in s_card_fqs
    assert "Lightning Bolt" in s_card_fqs
