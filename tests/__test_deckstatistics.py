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


def test_deckstatistics():
    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)
    archetype = "Burn"
    loader = AcademyDataLoader()
    deckstatistics = DeckstatisticsFactory(
        pauperformance.scryfall, loader
    ).build_metadata_for(archetype)
    staple, _ = deckstatistics.get_staple_and_frequent_cards()
    assert "Lightning Bolt" in staple
