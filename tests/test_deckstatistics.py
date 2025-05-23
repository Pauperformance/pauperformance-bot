from pauperformance_bot.service.academy.data_loader import AcademyDataLoader
from pauperformance_bot.service.pauperformance.archive.local import LocalArchiveService
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.deckstatistics import (
    DeckstatisticsFactory,
)
from pauperformance_bot.service.pauperformance.storage.local import LocalStorageService


def test_deckstatistics():
    storage = LocalStorageService()
    archive = LocalArchiveService()
    pauperformance = PauperformanceService(storage, archive)
    archetype = "Burn"
    loader = AcademyDataLoader()
    deckstatistics = DeckstatisticsFactory(
        pauperformance.scryfall, loader
    ).build_metadata_for(archetype)
    staple, _ = deckstatistics.get_staple_and_frequent_cards()
    assert "Lightning Bolt" in staple
