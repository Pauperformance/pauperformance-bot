from pauperformance_bot.constant.mtg.mtggoldfish import (
    DECK_API_ENDPOINT,
    DECK_DOWNLOAD_API_ENDPOINT,
)
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck


class MTGGoldfishArchivedDeck(AbstractArchivedDeck):
    def __init__(
        self,
        name: str,
        creation_date: int,
        deck_id: str,
        deck_api_endpoint: str = DECK_API_ENDPOINT,
        deck_download_api_endpoint: str = DECK_DOWNLOAD_API_ENDPOINT,
    ) -> None:
        super().__init__(name, creation_date, deck_id)
        self.deck_api_endpoint = deck_api_endpoint
        self.deck_download_api_endpoint = deck_download_api_endpoint

    @property
    def url(self) -> str:
        return f"{self.deck_api_endpoint}/{self.deck_id}"

    @property
    def download_txt_url(self) -> str:
        return f"{self.deck_download_api_endpoint}/{self.deck_id}"

    @property
    def download_tabletop_url(self) -> str:
        return (
            f"{self.deck_download_api_endpoint}/{self.deck_id}"
            f"?output=mtggoldfish&amp;type=tabletop"
        )

    @property
    def download_arena_url(self) -> str:
        return (
            f"{self.deck_download_api_endpoint}/{self.deck_id}"
            f"?output=mtggoldfish&amp;type=arena"
        )

    @property
    def download_mtgo_url(self) -> str:
        return (
            f"{self.deck_download_api_endpoint}/{self.deck_id}"
            f"?output=mtggoldfish&amp;type=online"
        )
