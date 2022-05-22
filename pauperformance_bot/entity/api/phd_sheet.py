from typing import Optional

from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class PhDSheet:
    def __init__(
        self,
        *,
        name: str,
        bio: str,
        mtgo_name: Optional[str],
        twitch_channel_url: Optional[str],
        youtube_channel_url: Optional[str],
        favorite_format: Optional[str],
        favorite_pauper_archetype: Optional[str],
        favorite_pauper_card_name: Optional[str],
        favorite_pauper_card_url: Optional[str],
        favorite_pauper_card_image_url: Optional[str],
        favorite_flavor_text_name: Optional[str],
        favorite_flavor_text_url: Optional[str],
        favorite_flavor_text_image_url: Optional[str],
        favorite_flavor_text_lines: Optional[str],
        favorite_artwork_name: Optional[str],
        favorite_artwork_url: Optional[str],
        favorite_artwork_image_url: Optional[str],
        favorite_artist_name: Optional[str],
        favorite_artist_gallery_url: Optional[str],
        favorite_magic_quote_lines: Optional[str],
    ):
        self.name: str = name
        self.bio: str = bio
        self.mtgo_name: Optional[str] = mtgo_name
        self.twitch_channel_url: Optional[str] = twitch_channel_url
        self.youtube_channel_url: Optional[str] = youtube_channel_url
        self.favorite_format: Optional[str] = favorite_format
        self.favorite_pauper_archetype: Optional[str] = favorite_pauper_archetype
        self.favorite_pauper_card_name: Optional[str] = favorite_pauper_card_name
        self.favorite_pauper_card_url: Optional[str] = favorite_pauper_card_url
        self.favorite_pauper_card_image_url: Optional[
            str
        ] = favorite_pauper_card_image_url
        self.favorite_flavor_text_name: Optional[str] = favorite_flavor_text_name
        self.favorite_flavor_text_url: Optional[str] = favorite_flavor_text_url
        self.favorite_flavor_text_image_url: Optional[
            str
        ] = favorite_flavor_text_image_url
        self.favorite_flavor_text_lines: Optional[str] = favorite_flavor_text_lines
        self.favorite_artwork_name: Optional[str] = favorite_artwork_name
        self.favorite_artwork_url: Optional[str] = favorite_artwork_url
        self.favorite_artwork_image_url: Optional[str] = favorite_artwork_image_url
        self.favorite_artist_name: Optional[str] = favorite_artist_name
        self.favorite_artist_gallery_url: Optional[str] = favorite_artist_gallery_url
        self.favorite_magic_quote_lines: Optional[str] = favorite_magic_quote_lines

    def __hash__(self) -> int:
        return hash(self.name)
