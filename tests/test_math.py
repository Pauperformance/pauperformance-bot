import unittest

from pauperformance_bot.util.math import truncate


class TestTruncate(unittest.TestCase):
    def test_truncate_positive_two_decimals(self):
        self.assertEqual(truncate(3.14159, 2), 3.14)

    def test_no_rounding_up(self):
        # 3.999 should truncate to 3.99, not round up to 4.0
        self.assertEqual(truncate(3.999, 2), 3.99)

    def test_truncate_zero_decimals(self):
        self.assertEqual(truncate(3.9, 0), 3.0)

    def test_truncate_negative(self):
        # truncates toward zero: -3.14159 -> -3.14
        self.assertEqual(truncate(-3.14159, 2), -3.14)

    def test_truncate_less_than_one(self):
        self.assertEqual(truncate(0.789, 2), 0.78)

    def test_truncate_pads_with_zeros(self):
        # 3.1 padded to 4 decimal places is still 3.1
        self.assertEqual(truncate(3.1, 4), 3.1)

    def test_truncate_exact_value_unchanged(self):
        self.assertEqual(truncate(2.50, 2), 2.5)


if __name__ == "__main__":
    unittest.main()
