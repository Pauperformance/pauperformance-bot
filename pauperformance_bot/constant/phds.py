from pauperformance_bot.constant.discord import (
    DISCORD_USER_HEISEN01_ID,
    DISCORD_USER_MREVILEYE_ID,
    DISCORD_USER_PAUPERGANDA_ID,
    DISCORD_USER_SHIKA93_ID,
    DISCORD_USER_TARMOGOYF_ITA_ID,
)
from pauperformance_bot.entity.phd import PhD

PAUPERFORMANCE = PhD(
    name="Pauperformance",
    mtgo_name="Pauperformance",
    deckstats_name="Pauperformance",
    deckstats_id="181430",
    twitch_login_name="Pauperformance",
    youtube_channel_id="UCDUiIskNnmuJ3XJ1SdQqs0A",
    default_youtube_language="en",
    discord_id=DISCORD_USER_SHIKA93_ID,
)

SHIKA93 = PhD(
    name="Shika93",
    mtgo_name="Shika93",
    deckstats_name="Shika93",
    deckstats_id="78813",
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
    discord_id=DISCORD_USER_SHIKA93_ID,
)

MREVILEYE = PhD(
    name="MrEvilEye",
    mtgo_name="MrEvilEye",
    deckstats_name="MrEvilEye",
    deckstats_id="72056",
    twitch_login_name=None,
    youtube_channel_id=None,
    default_youtube_language="en",
    discord_id=DISCORD_USER_MREVILEYE_ID,
)

PAUPERGANDA = PhD(
    name="PAUPERGANDA",
    mtgo_name="deluxeicoff",
    deckstats_name=None,
    deckstats_id=None,
    twitch_login_name="pauperganda",
    youtube_channel_id="UCqJ0E420KX9_3lFNJjDoKDA",
    default_youtube_language="en",
    discord_id=DISCORD_USER_PAUPERGANDA_ID,
)

TARMOGOYF_ITA = PhD(
    name="tarmogoyf_ita",
    mtgo_name="tarmogoyf_ita",
    deckstats_name="tarmogoyf_ita",
    deckstats_id="161568",
    twitch_login_name="lega_pauper_online",
    youtube_channel_id="UCAERb1O0w07LQ2ORO-N6V_Q",
    default_youtube_language="it",
    discord_id=DISCORD_USER_TARMOGOYF_ITA_ID,
)

HEISEN01 = PhD(
    name="Heisen01",
    mtgo_name="Heisen01",
    deckstats_name=None,
    deckstats_id=None,
    twitch_login_name="heisen01_",
    youtube_channel_id="UC1jO4Ge4jmlvaImhze5ldaw",
    default_youtube_language="it",
    discord_id=DISCORD_USER_HEISEN01_ID,
)

PAUPERFORMANCE_PHDS = [
    PAUPERFORMANCE,
    SHIKA93,
    MREVILEYE,
    PAUPERGANDA,
    TARMOGOYF_ITA,
    HEISEN01,
]
