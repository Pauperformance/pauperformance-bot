from pauperformance_bot.constant.api import DEFAULT_PHD_SHEET_EXPORT_DIR
from pauperformance_bot.entity.api.serializable import Serializable


class PhDSheet(Serializable):
    PATH = DEFAULT_PHD_SHEET_EXPORT_DIR

    def __init__(
            self,
            name,
            bio,
            mtgo_name,
            twitch_login_name,
            youtube_channel_id,
            favorite_format,
            favorite_pauper_archetype,
            favorite_pauper_card_name,
            favorite_pauper_card_image_url,
            favorite_flavor_text_card,
            favorite_flavor_text_url,
            favorite_flavor_text_lines,
            favorite_artwork_name,
            favorite_artwork_image_url,
            favorite_artist_name,
            favorite_artist_gallery_url,
            favorite_magic_quote_lines,
    ):
        self.name = name

    @property
    def path(self) -> str:
        return self.PATH

    @property
    def key(self) -> str:
        return self.name
