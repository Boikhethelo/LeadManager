import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import configparser
import ast

from database.creator import LeadConfig 


SAMPLE_CONFIG = """
[Files]
file1 = leads.csv
file2 = contacts.csv

[Fields]
leads = ['id', 'name', 'email']
contacts = ['id', 'phone', 'company']
"""

MISSING_FIELDS_CONFIG = """
[Files]
file1 = leads.csv

[Fields]
"""

EMPTY_FILES_CONFIG = """
[Files]

[Fields]
"""


class TestLeadConfigInit(unittest.TestCase):

    def test_default_path_is_set(self):
        config = LeadConfig()
        self.assertIsInstance(config.path, Path)
        self.assertTrue(str(config.path).endswith("config.ini"))

    def test_custom_path_is_set(self):
        custom_path = Path("/some/custom/path/config.ini")
        config = LeadConfig(config_path=custom_path)
        self.assertEqual(config.path, custom_path)

    def test_string_path_is_converted_to_path(self):
        config = LeadConfig(config_path="/some/path/config.ini")
        self.assertIsInstance(config.path, Path)


class TestLeadConfigGetDefinitions(unittest.TestCase):

    def _make_config(self, config_string: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read_string(config_string)
        return config

    def test_returns_list(self):
        config = LeadConfig(config_path="/fake/path/config.ini")
        with patch("configparser.ConfigParser.read"):
            with patch.object(configparser.ConfigParser, "read"):
                cp = self._make_config(SAMPLE_CONFIG)
                with patch("configparser.ConfigParser.__getitem__", side_effect=cp.__getitem__):
                    with patch("configparser.ConfigParser.read", lambda self, path: cp.read_string(SAMPLE_CONFIG)):
                        result = config.get_definitions()
        self.assertIsInstance(result, list)

    def _patch_and_run(self, config_string: str) -> list[dict]:
        """Helper: patch configparser.read so it loads config_string, then call get_definitions."""
        config = LeadConfig(config_path="/fake/path/config.ini")
        cp = configparser.ConfigParser()
        cp.read_string(config_string)

        with patch.object(configparser.ConfigParser, "read", lambda self, path: self.read_string(config_string)):
            result = config.get_definitions()
        return result

    def test_returns_correct_number_of_entries(self):
        result = self._patch_and_run(SAMPLE_CONFIG)
        self.assertEqual(len(result), 2)

    def test_entry_has_required_keys(self):
        result = self._patch_and_run(SAMPLE_CONFIG)
        for entry in result:
            self.assertIn("filename", entry)
            self.assertIn("header", entry)
            self.assertIn("key", entry)

    def test_filename_values(self):
        result = self._patch_and_run(SAMPLE_CONFIG)
        filenames = {entry["filename"] for entry in result}
        self.assertEqual(filenames, {"leads.csv", "contacts.csv"})

    def test_key_is_filename_without_csv_suffix(self):
        result = self._patch_and_run(SAMPLE_CONFIG)
        for entry in result:
            self.assertEqual(entry["key"], entry["filename"].removesuffix(".csv"))

    def test_header_is_parsed_correctly(self):
        result = self._patch_and_run(SAMPLE_CONFIG)
        entry_map = {e["key"]: e for e in result}
        self.assertEqual(entry_map["leads"]["header"], ["id", "name", "email"])
        self.assertEqual(entry_map["contacts"]["header"], ["id", "phone", "company"])

    def test_missing_field_section_entry_defaults_to_empty_list(self):
        result = self._patch_and_run(MISSING_FIELDS_CONFIG)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["header"], [])
        self.assertEqual(result[0]["filename"], "leads.csv")
        self.assertEqual(result[0]["key"], "leads")

    def test_empty_files_section_returns_empty_list(self):
        result = self._patch_and_run(EMPTY_FILES_CONFIG)
        self.assertEqual(result, [])

    def test_header_is_always_a_list(self):
        result = self._patch_and_run(SAMPLE_CONFIG)
        for entry in result:
            self.assertIsInstance(entry["header"], list)

    def test_path_is_passed_to_config_read(self):
        fake_path = Path("/fake/path/config.ini")
        config = LeadConfig(config_path=fake_path)

        with patch("configparser.ConfigParser.read") as mock_read:
            with patch("configparser.ConfigParser.__getitem__", return_value={}):
                try:
                    config.get_definitions()
                except Exception:
                    pass
            mock_read.assert_called_once_with(fake_path)


if __name__ == "__main__":
    unittest.main()