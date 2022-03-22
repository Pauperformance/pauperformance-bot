from pauperformance_bot.credentials import (
    TELEGRAM_CHUMPBLOCCKAMI_ID,
    TELEGRAM_MIKEOSCAR_ID,
    TELEGRAM_MREVILEYE_ID,
    TELEGRAM_PAUPERFORMANCE_ID,
    TELEGRAM_RIKXVIS_ID,
    TELEGRAM_SHIKA93_ID,
    TELEGRAM_THRABEN27_ID, TELEGRAM_TARMOGOYF_ITA_ID,
)
from pauperformance_bot.entity.pauperformance_player import (
    PauperformancePlayer,
)

PAUPERFORMANCE_PLAYER = PauperformancePlayer(
    name="Pauperformance",
    mtgo_name="Pauperformance",
    deckstats_name="Pauperformance",
    deckstats_id="181430",
    telegram_id=TELEGRAM_PAUPERFORMANCE_ID,
    twitch_login_name="Pauperformance",
    youtube_channel_id="UCDUiIskNnmuJ3XJ1SdQqs0A",
    default_youtube_language="en",
)

SHIKA93_PLAYER = PauperformancePlayer(
    name="Shika93",
    mtgo_name="Shika93",
    deckstats_name="Shika93",
    deckstats_id="78813",
    telegram_id=TELEGRAM_SHIKA93_ID,
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
)

MREVILEYE_PLAYER = PauperformancePlayer(
    name="MrEvilEye",
    mtgo_name="MrEvilEye",
    deckstats_name="MrEvilEye",
    deckstats_id="72056",
    telegram_id=TELEGRAM_MREVILEYE_ID,
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
)

MIKEOSCAR_PLAYER = PauperformancePlayer(
    name="MikeOscar",
    mtgo_name=None,
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=TELEGRAM_MIKEOSCAR_ID,
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
)

THRABEN27_PLAYER = PauperformancePlayer(
    name="Thraben27",
    mtgo_name="Thraben27",
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=TELEGRAM_THRABEN27_ID,
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
)

RIKXVIS_PLAYER = PauperformancePlayer(
    name="Rikxvis",
    mtgo_name=None,
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=TELEGRAM_RIKXVIS_ID,
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
)

CHUMPBLOCCKAMI_PLAYER = PauperformancePlayer(
    name="chumpblocckami",
    mtgo_name="chumpblocckami",
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=TELEGRAM_CHUMPBLOCCKAMI_ID,
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
)

PAUPERGANDA_PLAYER = PauperformancePlayer(
    name="PAUPERGANDA",
    mtgo_name="deluxeicoff",
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=None,
    twitch_login_name='pauperganda',
    youtube_channel_id='UCqJ0E420KX9_3lFNJjDoKDA',
    default_youtube_language="en",
)

TARMOGOYF_ITA_PLAYER = PauperformancePlayer(
    name="tarmogoyf_ita",
    mtgo_name="tarmogoyf_ita",
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=TELEGRAM_TARMOGOYF_ITA_ID,
    twitch_login_name='lega_pauper_online',
    youtube_channel_id='UCAERb1O0w07LQ2ORO-N6V_Q',
    default_youtube_language="it",
)

PAUPERFORMANCE_PLAYERS = [
    PAUPERFORMANCE_PLAYER,
    SHIKA93_PLAYER,
    MREVILEYE_PLAYER,
    MIKEOSCAR_PLAYER,
    THRABEN27_PLAYER,
    RIKXVIS_PLAYER,
    CHUMPBLOCCKAMI_PLAYER,
    TARMOGOYF_ITA_PLAYER,
]
