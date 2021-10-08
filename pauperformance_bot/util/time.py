import time

from datetime import datetime

from pauperformance_bot.constant.myr import DEFAULT_DATE_FORMAT


def now():
    return int(round(time.time() * 1000))


def pretty_str(now_ms: int, date_format=DEFAULT_DATE_FORMAT):
    now_dt = datetime.fromtimestamp(now_ms / 1000.0)
    return now_dt.strftime(date_format)
