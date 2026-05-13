import os
import tempfile
import unittest
import warnings

from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.util.config import (
    _parse_list_value,
    read_archetype_config,
    read_family_config,
)


def _write_ini(tmpdir, filename, content):
    path = os.path.join(tmpdir, filename)
    with open(path, "w") as f:
        f.write(content)
    return path


class TestParseListValue(unittest.TestCase):
    def test_empty_string(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertEqual(_parse_list_value(""), [])

    def test_single_value(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertEqual(_parse_list_value("Burn"), ["Burn"])

    def test_multiple_values(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = _parse_list_value("Burn, Faeries, Affinity")
            self.assertEqual(result, ["Burn", "Faeries", "Affinity"])

    def test_strips_spaces(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = _parse_list_value("  Burn  ,  Faeries  ")
            self.assertEqual(result, ["Burn", "Faeries"])


class TestReadFamilyConfig(unittest.TestCase):
    def test_reads_values_section(self):
        ini_content = "[values]\nname = Aggro\ncolor = red\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = _write_ini(tmpdir, "family.ini", ini_content)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_family_config(path)
        self.assertEqual(result["name"], "Aggro")
        self.assertEqual(result["color"], "red")


class TestReadArchetypeConfig(unittest.TestCase):
    def _write_archetype_ini(self, tmpdir, extra=""):
        ini_content = (
            "[values]\n"
            "name = Burn\n"
            "aliases = \n"
            "mana = R\n"
            "type = aggro\n"
            "\n"
            "[references]\n"
            "100 = Burn 100.001.Player\n"
            "\n" + extra
        )
        return _write_ini(tmpdir, "burn.ini", ini_content)

    def test_reads_values_and_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_archetype_ini(tmpdir)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_archetype_config(path)
        self.assertEqual(result["values"]["name"], "Burn")
        self.assertIn("100", result["references"])

    def test_list_fields_parsed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_archetype_ini(tmpdir)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_archetype_config(path)
        self.assertIsInstance(result["values"]["aliases"], list)
        self.assertIsInstance(result["values"]["mana"], list)
        self.assertIsInstance(result["values"]["type"], list)

    def test_no_resources_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_archetype_ini(tmpdir)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_archetype_config(path)
        self.assertEqual(result["resources"], [])

    def test_with_resource_section(self):
        resource_section = (
            "[resource1]\n"
            "url = https://example.com\n"
            "name = Burn Guide\n"
            "language = en\n"
            "date = 2023-01-01\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_archetype_ini(tmpdir, extra=resource_section)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_archetype_config(path)
        resources = result["resources"]
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["url"], "https://example.com")

    def test_mismatched_reference_key_raises(self):
        # key "200" does not appear in deck name "Burn 100.001.Player"
        bad_ini = (
            "[values]\n"
            "name = Burn\n"
            "aliases = \n"
            "mana = R\n"
            "type = aggro\n"
            "\n"
            "[references]\n"
            "200 = Burn 100.001.Player\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = _write_ini(tmpdir, "bad.ini", bad_ini)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                with self.assertRaises(PauperformanceException):
                    read_archetype_config(path)

    def test_with_discord_section(self):
        discord_section = (
            "[discord1]\nurl = https://discord.gg/abc\nname = Burn Discord\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_archetype_ini(tmpdir, extra=discord_section)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_archetype_config(path)
        discord_resources = [
            r for r in result["resources"] if "discord" in r.get("url", "")
        ]
        self.assertEqual(len(discord_resources), 1)
        self.assertIn("discord", discord_resources[0]["author"])
        self.assertEqual(discord_resources[0]["date"], "~")

    def test_with_sideboard_section(self):
        sideboard_section = "[sideboard]\nurl = https://example.com/sideboard\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_archetype_ini(tmpdir, extra=sideboard_section)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = read_archetype_config(path)
        resource_names = [r["name"] for r in result["resources"]]
        self.assertIn("**Sideboard Guide**", resource_names)


if __name__ == "__main__":
    unittest.main()
