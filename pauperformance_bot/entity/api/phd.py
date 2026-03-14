from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
@auto_str
class PhDSheet:
    def __init__(
        self,
        *,
        name: str,
        bio: str,
        mtgo_name: str | None,
        twitch_channel_url: str | None,
        youtube_channel_url: str | None,
        favorite_format: str | None,
        favorite_pauper_archetype: str | None,
        favorite_pauper_card_name: str | None,
        favorite_pauper_card_url: str | None,
        favorite_pauper_card_image_url: str | None,
        favorite_flavor_text_name: str | None,
        favorite_flavor_text_url: str | None,
        favorite_flavor_text_image_url: str | None,
        favorite_flavor_text_lines: str | None,
        favorite_artwork_name: str | None,
        favorite_artwork_url: str | None,
        favorite_artwork_image_url: str | None,
        favorite_artist_name: str | None,
        favorite_artist_gallery_url: str | None,
        favorite_magic_quote_lines: str | None,
    ) -> None:
        self.name = name
        self.bio = bio
        self.mtgo_name = mtgo_name
        self.twitch_channel_url = twitch_channel_url
        self.youtube_channel_url = youtube_channel_url
        self.favorite_format = favorite_format
        self.favorite_pauper_archetype = favorite_pauper_archetype
        self.favorite_pauper_card_name = favorite_pauper_card_name
        self.favorite_pauper_card_url = favorite_pauper_card_url
        self.favorite_pauper_card_image_url = favorite_pauper_card_image_url
        self.favorite_flavor_text_name = favorite_flavor_text_name
        self.favorite_flavor_text_url = favorite_flavor_text_url
        self.favorite_flavor_text_image_url = favorite_flavor_text_image_url
        self.favorite_flavor_text_lines = favorite_flavor_text_lines
        self.favorite_artwork_name = favorite_artwork_name
        self.favorite_artwork_url = favorite_artwork_url
        self.favorite_artwork_image_url = favorite_artwork_image_url
        self.favorite_artist_name = favorite_artist_name
        self.favorite_artist_gallery_url = favorite_artist_gallery_url
        self.favorite_magic_quote_lines = favorite_magic_quote_lines

    def __hash__(self) -> int:
        return hash(self.name)
