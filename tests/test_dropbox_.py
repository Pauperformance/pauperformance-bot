import pytest

from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService


@pytest.mark.integration
def test_list_imported_youtube_videos():
    assert any(
        "Pauperformance" in v for v in DropboxService().list_imported_youtube_videos()
    )


@pytest.mark.integration
def test_list_imported_mtggoldfish_deck_names():
    assert any(
        "Jund" in d for d in DropboxService().list_imported_mtggoldfish_deck_names()
    )
