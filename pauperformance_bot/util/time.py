import time
from datetime import datetime

from pauperformance_bot.constant.pauperformance.myr import (
    DEFAULT_DATE_FORMAT,
    USA_DATE_FORMAT,
)


def now():
    return int(round(time.time() * 1000))


def now_utc() -> int:
    # please note this function does not always return the same value of now(),
    # because the local timezone (used by now()) can be different (e.g. 'CET').
    return datetime_to_ms(datetime.utcnow())


def datetime_to_ms(dt):
    return int(dt.timestamp() * 1000)


def pretty_str(now_ms: int, date_format=DEFAULT_DATE_FORMAT):
    now_dt = datetime.fromtimestamp(now_ms / 1000.0)
    return now_dt.strftime(date_format)


def simple_str(now_ms: int, date_format=USA_DATE_FORMAT):
    now_dt = datetime.fromtimestamp(now_ms / 1000.0)
    return now_dt.strftime(date_format)
