import os
import tempfile
import unittest

from pauperformance_bot.util.path import (
    load_json_from_file,
    posix_path,
    safe_dump_json_to_file,
)


class TestPosixPath(unittest.TestCase):
    def test_joins_multiple_parts(self):
        self.assertEqual(posix_path("a", "b", "c"), "a/b/c")

    def test_single_part(self):
        self.assertEqual(posix_path("a"), "a")

    def test_nested(self):
        self.assertEqual(posix_path("root", "sub", "file.txt"), "root/sub/file.txt")


class TestDumpAndLoadJson(unittest.TestCase):
    def test_round_trip_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj = {"key": "value", "number": 42}
            safe_dump_json_to_file(tmpdir, "test.json", obj)
            loaded = load_json_from_file(os.path.join(tmpdir, "test.json"))
            self.assertEqual(loaded, obj)

    def test_round_trip_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj = [1, 2, 3]
            safe_dump_json_to_file(tmpdir, "list.json", obj)
            loaded = load_json_from_file(os.path.join(tmpdir, "list.json"))
            self.assertEqual(loaded, obj)

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_dump_json_to_file(tmpdir, "out.json", {})
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "out.json")))

    def test_creates_missing_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "a", "b", "c")
            safe_dump_json_to_file(nested, "f.json", {})
            self.assertTrue(os.path.isdir(nested))


if __name__ == "__main__":
    unittest.main()
