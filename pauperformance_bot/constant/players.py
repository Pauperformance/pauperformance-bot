from pauperformance_bot.credentials import (
    TELEGRAM_MREVILEYE_ID,
    TELEGRAM_PAUPERFORMANCE_ID,
    TELEGRAM_SHIKA93_ID,
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
)

SHIKA93_PLAYER = PauperformancePlayer(
    name="Shika93",
    mtgo_name="Shika93",
    deckstats_name="Shika93",
    deckstats_id="78813",
    telegram_id=TELEGRAM_SHIKA93_ID,
)

MREVILEYE_PLAYER = PauperformancePlayer(
    name="MrEvilEye",
    mtgo_name="MrEvilEye",
    deckstats_name="MrEvilEye",
    deckstats_id="72056",
    telegram_id=TELEGRAM_MREVILEYE_ID,
)

PAUPERFORMANCE_PLAYERS = [
    PAUPERFORMANCE_PLAYER,
    SHIKA93_PLAYER,
    MREVILEYE_PLAYER,
]
