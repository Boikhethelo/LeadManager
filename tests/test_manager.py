import os
import unittest
from unittest.mock import MagicMock, patch, call

from database.manager import LeadManager



def make_handler(directory="/tmp/leads"):
    handler = MagicMock()
    handler.directory = directory
    return handler


def make_config(definitions=None):
    config = MagicMock()
    if definitions is None:
        definitions = [
            {"key": "contacts", "filename": "contacts.csv", "header": ["ID", "Name", "Email"]},
            {"key": "notes",    "filename": "notes.csv",    "header": ["ID", "Note"]},
        ]
    config.get_definitions.return_value = definitions
    return config


class TestLeadManagerInitializeSystem(unittest.TestCase):

    @patch("os.path.exists")
    def test_creates_missing_files(self, mock_exists):
        """Files that don't exist on disk should be created via write_file."""
        mock_exists.return_value = False
        handler = make_handler()
        handler.read_file.return_value = []
        config = make_config()

        manager = manager.LeadManager(handler, config)
        manager.initialize_system()

        expected_write_calls = [
            call("contacts.csv", ["ID", "Name", "Email"]),
            call("notes.csv",    ["ID", "Note"]),
        ]
        handler.write_file.assert_has_calls(expected_write_calls, any_order=False)

    @patch("os.path.exists")
    def test_does_not_create_existing_files(self, mock_exists):
        """Files that already exist on disk should NOT be passed to write_file."""
        mock_exists.return_value = True
        handler = make_handler()
        handler.read_file.return_value = []
        config = make_config()

        manager = LeadManager(handler, config)
        manager.initialize_system()

        handler.write_file.assert_not_called()

    @patch("os.path.exists")
    def test_data_keys_populated_after_init(self, mock_exists):
        """self.data should be keyed by field 'key' after initialize_system."""
        mock_exists.return_value = True
        handler = make_handler()
        handler.read_file.side_effect = lambda filename: (
            [{"ID": "1", "Name": "Alice"}] if "contacts" in filename else [{"ID": "1", "Note": "hi"}]
        )
        config = make_config()

        manager = LeadManager(handler, config)
        manager.initialize_system()

        self.assertIn("contacts", manager.data)
        self.assertIn("notes",    manager.data)

    @patch("os.path.exists")
    def test_read_file_called_for_each_field(self, mock_exists):
        """read_file should be called once per field definition."""
        mock_exists.return_value = True
        handler = make_handler()
        handler.read_file.return_value = []
        config = make_config()

        manager = LeadManager(handler, config)
        manager.initialize_system()

        self.assertEqual(handler.read_file.call_count, 2)

    @patch("os.path.exists")
    def test_full_path_used_for_exists_check(self, mock_exists):
        """os.path.exists should be called with the joined directory + filename."""
        mock_exists.return_value = True
        handler = make_handler(directory="/data/leads")
        handler.read_file.return_value = []
        config = make_config()

        manager = LeadManager(handler, config)
        manager.initialize_system()

        checked_paths = [c.args[0] for c in mock_exists.call_args_list]
        self.assertIn("/data/leads/contacts.csv", checked_paths)
        self.assertIn("/data/leads/notes.csv",    checked_paths)

    @patch("os.path.exists")
    def test_mixed_existing_and_missing_files(self, mock_exists):
        """Only missing files should be created; existing ones should only be read."""
        mock_exists.side_effect = lambda path: "contacts" in path  # contacts exists, notes doesn't
        handler = make_handler()
        handler.read_file.return_value = []
        config = make_config()

        manager = LeadManager(handler, config)
        manager.initialize_system()

        # write_file should only be called for notes.csv
        handler.write_file.assert_called_once_with("notes.csv", ["ID", "Note"])

    @patch("os.path.exists")
    def test_empty_definitions(self, mock_exists):
        """initialize_system with no field definitions should leave data empty."""
        handler = make_handler()
        config = make_config(definitions=[])

        manager = LeadManager(handler, config)
        manager.initialize_system()

        self.assertEqual(manager.data, {})
        handler.write_file.assert_not_called()
        handler.read_file.assert_not_called()


class TestLeadManagerSearchById(unittest.TestCase):

    def _manager_with_data(self, data: dict) -> LeadManager:
        handler = make_handler()
        config = make_config()
        manager = LeadManager(handler, config)
        manager.data = data
        return manager

    def test_returns_matching_lead(self):
        """search_by_id should return rows whose ID matches the query."""
        manager = self._manager_with_data({
            "contacts": [{"ID": "42", "Name": "Alice"}, {"ID": "99", "Name": "Bob"}],
        })
        result = manager.search_by_id("42")
        self.assertEqual(result["contacts"], [{"ID": "42", "Name": "Alice"}])

    def test_returns_empty_list_for_no_match(self):
        """search_by_id should return an empty list when no row matches."""
        manager = self._manager_with_data({
            "contacts": [{"ID": "1", "Name": "Alice"}],
        })
        result = manager.search_by_id("999")
        self.assertEqual(result["contacts"], [])

    def test_all_categories_present_in_result(self):
        """Result dict should contain a key for every category even if no matches."""
        manager = self._manager_with_data({
            "contacts": [{"ID": "1", "Name": "Alice"}],
            "notes":    [{"ID": "2", "Note": "nothing"}],
        })
        result = manager.search_by_id("1")
        self.assertIn("contacts", result)
        self.assertIn("notes",    result)
        self.assertEqual(result["notes"], [])

    def test_multiple_matches_in_same_category(self):
        """search_by_id should return all matching rows, not just the first."""
        manager = self._manager_with_data({
            "notes": [
                {"ID": "5", "Note": "first"},
                {"ID": "5", "Note": "second"},
                {"ID": "9", "Note": "other"},
            ]
        })
        result = manager.search_by_id("5")
        self.assertEqual(len(result["notes"]), 2)

    def test_matches_across_multiple_categories(self):
        """Matches should be found independently in each category."""
        manager = self._manager_with_data({
            "contacts": [{"ID": "7", "Name": "Carol"}],
            "notes":    [{"ID": "7", "Note": "VIP"}],
        })
        result = manager.search_by_id("7")
        self.assertEqual(result["contacts"], [{"ID": "7", "Name": "Carol"}])
        self.assertEqual(result["notes"],    [{"ID": "7", "Note": "VIP"}])

    def test_empty_data_returns_empty_categories(self):
        """search_by_id on empty data should return a dict with empty lists."""
        manager = self._manager_with_data({
            "contacts": [],
            "notes":    [],
        })
        result = manager.search_by_id("1")
        self.assertEqual(result, {"contacts": [], "notes": []})

    def test_empty_manager_data(self):
        """search_by_id when data is entirely empty should return an empty dict."""
        manager = self._manager_with_data({})
        result = manager.search_by_id("1")
        self.assertEqual(result, {})

    def test_row_missing_id_field_is_skipped(self):
        """Rows without an 'ID' key should not cause errors and not be returned."""
        manager = self._manager_with_data({
            "contacts": [{"Name": "No-ID person"}, {"ID": "3", "Name": "With ID"}],
        })
        result = manager.search_by_id("3")
        self.assertEqual(result["contacts"], [{"ID": "3", "Name": "With ID"}])

    def test_id_matching_is_exact(self):
        """ID lookup should be exact; substrings should not match."""
        manager = self._manager_with_data({
            "contacts": [{"ID": "123", "Name": "Alice"}, {"ID": "12", "Name": "Bob"}],
        })
        result = manager.search_by_id("12")
        self.assertEqual(result["contacts"], [{"ID": "12", "Name": "Bob"}])


if __name__ == "__main__":
    unittest.main()