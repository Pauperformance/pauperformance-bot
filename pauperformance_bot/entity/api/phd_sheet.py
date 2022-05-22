from pauperformance_bot.util.entities import auto_repr, auto_str


@auto_repr
@auto_str
class PhDSheet:
    def __init__(
        self,
        *,
        name: str,
        bio: str,
        mtgo_name: str,
        twitch_channel_url: str,
        youtube_channel_url: str,
        favorite_format: str,
        favorite_pauper_archetype: str,
        favorite_pauper_card_name: str,
        favorite_pauper_card_url: str,
        favorite_pauper_card_image_url: str,
        favorite_flavor_text_name: str,
        favorite_flavor_text_url: str,
        favorite_flavor_text_image_url: str,
        favorite_flavor_text_lines: str,
        favorite_artwork_name: str,
        favorite_artwork_url: str,
        favorite_artwork_image_url: str,
        favorite_artist_name: str,
        favorite_artist_gallery_url: str,
        favorite_magic_quote_lines: str,
    ):
        self.name: str = name
        self.bio: str = bio
        self.mtgo_name: str = mtgo_name
        self.twitch_channel_url: str = twitch_channel_url
        self.youtube_channel_url: str = youtube_channel_url
        self.favorite_format: str = favorite_format
        self.favorite_pauper_archetype: str = favorite_pauper_archetype

        self.favorite_pauper_card_name: str = favorite_pauper_card_name
        self.favorite_pauper_card_url: str = favorite_pauper_card_url
        self.favorite_pauper_card_image_url: str = favorite_pauper_card_image_url

        self.favorite_flavor_text_name: str = favorite_flavor_text_name
        self.favorite_flavor_text_url: str = favorite_flavor_text_url
        self.favorite_flavor_text_image_url: str = favorite_flavor_text_image_url
        self.favorite_flavor_text_lines: str = favorite_flavor_text_lines

        self.favorite_artwork_name: str = favorite_artwork_name
        self.favorite_artwork_url: str = favorite_artwork_url
        self.favorite_artwork_image_url: str = favorite_artwork_image_url

        self.favorite_artist_name: str = favorite_artist_name
        self.favorite_artist_gallery_url: str = favorite_artist_gallery_url
        self.favorite_magic_quote_lines: str = favorite_magic_quote_lines

    def __hash__(self) -> int:
        return hash(self.name)
