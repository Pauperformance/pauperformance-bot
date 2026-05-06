import unittest

from requests import ConnectionError

from pauperformance_bot.util.request import _retry_on_connection_error


class TestRetryOnConnectionError(unittest.TestCase):
    def test_returns_true_for_connection_error(self):
        self.assertTrue(_retry_on_connection_error(ConnectionError("timeout")))

    def test_returns_false_for_value_error(self):
        self.assertFalse(
            _retry_on_connection_error(ValueError("not a connection error"))
        )

    def test_returns_false_for_runtime_error(self):
        self.assertFalse(_retry_on_connection_error(RuntimeError("something")))


if __name__ == "__main__":
    unittest.main()
