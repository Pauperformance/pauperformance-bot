from pauperformance_bot.credentials import (
    DISCORD_USER_MREVILEYE_ID,
    DISCORD_USER_SHIKA93_ID,
    TELEGRAM_CHUMPBLOCCKAMI_ID,
    TELEGRAM_MIKEOSCAR_ID,
    TELEGRAM_MREVILEYE_ID,
    TELEGRAM_PAUPERFORMANCE_ID,
    TELEGRAM_RIKXVIS_ID,
    TELEGRAM_SHIKA93_ID,
    TELEGRAM_TARMOGOYF_ITA_ID,
    TELEGRAM_THRABEN27_ID,
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
    discord_id=None,
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
    discord_id=DISCORD_USER_SHIKA93_ID,
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
    discord_id=DISCORD_USER_MREVILEYE_ID,
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
    discord_id=None,
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
    discord_id=None,
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
    discord_id=None,
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
    discord_id=None,
)

PAUPERGANDA_PLAYER = PauperformancePlayer(
    name="PAUPERGANDA",
    mtgo_name="deluxeicoff",
    deckstats_name=None,
    deckstats_id=None,
    telegram_id=None,
    twitch_login_name="pauperganda",
    youtube_channel_id="UCqJ0E420KX9_3lFNJjDoKDA",
    default_youtube_language="en",
    discord_id=None,
)

TARMOGOYF_ITA_PLAYER = PauperformancePlayer(
    name="tarmogoyf_ita",
    mtgo_name="tarmogoyf_ita",
    deckstats_name="tarmogoyf_ita",
    deckstats_id="161568",
    telegram_id=TELEGRAM_TARMOGOYF_ITA_ID,
    twitch_login_name="lega_pauper_online",
    youtube_channel_id="UCAERb1O0w07LQ2ORO-N6V_Q",
    default_youtube_language="it",
    discord_id=None,
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
    PAUPERGANDA_PLAYER,
]
