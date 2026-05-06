import unittest
from datetime import datetime

from pauperformance_bot.util.time import (
    datetime_to_ms,
    now,
    now_utc,
    pretty_str,
    simple_str,
)


class TestNow(unittest.TestCase):
    def test_returns_int(self):
        self.assertIsInstance(now(), int)

    def test_is_positive(self):
        self.assertGreater(now(), 0)

    def test_increases_over_time(self):
        t1 = now()
        t2 = now()
        self.assertGreaterEqual(t2, t1)


class TestNowUtc(unittest.TestCase):
    def test_returns_int(self):
        self.assertIsInstance(now_utc(), int)

    def test_is_positive(self):
        self.assertGreater(now_utc(), 0)

    def test_close_to_now(self):
        t_local = now()
        t_utc = now_utc()
        # allow up to 13 hours difference to account for any timezone
        self.assertLess(abs(t_local - t_utc), 13 * 3600 * 1000)


class TestDatetimeToMs(unittest.TestCase):
    def test_round_trip(self):
        dt = datetime(2023, 6, 15, 10, 30, 0)
        ms = datetime_to_ms(dt)
        self.assertEqual(datetime.fromtimestamp(ms / 1000.0), dt)

    def test_returns_int(self):
        ms = datetime_to_ms(datetime(2023, 1, 1))
        self.assertIsInstance(ms, int)

    def test_millisecond_precision(self):
        dt1 = datetime(2023, 1, 1, 0, 0, 0)
        dt2 = datetime(2023, 1, 1, 0, 0, 1)
        self.assertEqual(datetime_to_ms(dt2) - datetime_to_ms(dt1), 1000)


class TestPrettyStr(unittest.TestCase):
    def test_format(self):
        dt = datetime(2023, 6, 15, 12, 30, 45)
        ms = int(dt.timestamp() * 1000)
        self.assertEqual(pretty_str(ms), "2023-06-15, 12:30:45")

    def test_midnight(self):
        dt = datetime(2023, 1, 1, 0, 0, 0)
        ms = int(dt.timestamp() * 1000)
        self.assertEqual(pretty_str(ms), "2023-01-01, 00:00:00")

    def test_custom_format(self):
        dt = datetime(2023, 6, 15, 12, 30, 45)
        ms = int(dt.timestamp() * 1000)
        self.assertEqual(pretty_str(ms, date_format="%d/%m/%Y"), "15/06/2023")


class TestSimpleStr(unittest.TestCase):
    def test_date_only_format(self):
        dt = datetime(2023, 6, 15, 12, 30, 45)
        ms = int(dt.timestamp() * 1000)
        self.assertEqual(simple_str(ms), "2023-06-15")

    def test_time_stripped(self):
        dt1 = datetime(2023, 6, 15, 0, 0, 0)
        dt2 = datetime(2023, 6, 15, 23, 59, 59)
        ms1 = int(dt1.timestamp() * 1000)
        ms2 = int(dt2.timestamp() * 1000)
        # same date regardless of time
        self.assertEqual(simple_str(ms1), simple_str(ms2))


if __name__ == "__main__":
    unittest.main()
