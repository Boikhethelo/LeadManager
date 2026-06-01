import os
import unittest
from unittest.mock import MagicMock, patch, call

from database.csv_repository import CsvLeadRepository


def make_handler(directory="/tmp/leads"):
    handler = MagicMock()
    handler.directory = directory
    return handler


def make_config(definitions=None):
    config = MagicMock()
    if definitions is None:
        definitions = [
            {"key": "leads",        "filename": "leads.csv",        "header": ["ID", "Status", "Source"]},
            {"key": "contacts",     "filename": "contacts.csv",     "header": ["ID", "Name", "Role"]},
            {"key": "companies",    "filename": "company.csv",    "header": ["ID", "Name", "Industry"]},
            {"key": "interactions", "filename": "interactions.csv", "header": ["ID", "Date", "Notes"]},
        ]
    config.get_definitions.return_value = definitions
    return config


def make_repo(data=None):
    handler = make_handler()
    config = make_config()
    repo = CsvLeadRepository(handler, config)
    if data is not None:
        repo.data = data
    return repo


# ---------------------------------------------------------------------------
# ensure_loaded
# ---------------------------------------------------------------------------

class TestEnsureLoaded(unittest.TestCase):

    @patch("os.path.exists")
    def test_skips_if_data_already_populated(self, mock_exists):
        repo = make_repo(data={"leads": [{"ID": "1"}]})
        repo.ensure_loaded()
        repo.handler.read_file.assert_not_called()

    @patch("os.path.exists")
    def test_reads_all_files_on_first_load(self, mock_exists):
        mock_exists.return_value = True
        handler = make_handler()
        handler.read_file.return_value = []
        repo = CsvLeadRepository(handler, make_config())
        repo.ensure_loaded()
        assert handler.read_file.call_count == 4

    @patch("os.path.exists")
    def test_creates_missing_files(self, mock_exists):
        mock_exists.return_value = False
        handler = make_handler()
        handler.read_file.return_value = []
        repo = CsvLeadRepository(handler, make_config())
        repo.ensure_loaded()
        assert handler.write_file.call_count == 4

    @patch("os.path.exists")
    def test_does_not_create_existing_files(self, mock_exists):
        mock_exists.return_value = True
        handler = make_handler()
        handler.read_file.return_value = []
        repo = CsvLeadRepository(handler, make_config())
        repo.ensure_loaded()
        handler.write_file.assert_not_called()

    @patch("os.path.exists")
    def test_data_keys_match_config_keys(self, mock_exists):
        mock_exists.return_value = True
        handler = make_handler()
        handler.read_file.return_value = []
        repo = CsvLeadRepository(handler, make_config())
        repo.ensure_loaded()
        self.assertIn("leads", repo.data)
        self.assertIn("contacts", repo.data)
        self.assertIn("companies", repo.data)
        self.assertIn("interactions", repo.data)

    @patch("os.path.exists")
    def test_full_path_used_for_exists_check(self, mock_exists):
        mock_exists.return_value = True
        handler = make_handler(directory="/data/leads")
        handler.read_file.return_value = []
        repo = CsvLeadRepository(handler, make_config())
        repo.ensure_loaded()
        checked = [c.args[0] for c in mock_exists.call_args_list]
        self.assertIn("/data/leads/leads.csv", checked)

    @patch("os.path.exists")
    def test_mixed_existing_and_missing(self, mock_exists):
        mock_exists.side_effect = lambda path: "leads" in path
        handler = make_handler()
        handler.read_file.return_value = []
        config = make_config([
            {"key": "leads",    "filename": "leads.csv",    "header": ["ID", "Status"]},
            {"key": "contacts", "filename": "contacts.csv", "header": ["ID", "Name"]},
        ])
        repo = CsvLeadRepository(handler, config)
        repo.ensure_loaded()
        handler.write_file.assert_called_once_with("contacts.csv", ["ID", "Name"])


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------

class TestGetAll(unittest.TestCase):

    def test_returns_correct_category(self):
        repo = make_repo(data={"leads": [{"ID": "1", "Status": "New"}]})
        result = repo.get_all("leads")
        self.assertEqual(result, [{"ID": "1", "Status": "New"}])

    def test_returns_empty_list_for_missing_category(self):
        repo = make_repo(data={})
        result = repo.get_all("leads")
        self.assertEqual(result, [])

    def test_returns_empty_list_for_empty_category(self):
        repo = make_repo(data={"leads": []})
        result = repo.get_all("leads")
        self.assertEqual(result, [])

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": []})
        repo.ensure_loaded = MagicMock()
        repo.get_all("leads")
        repo.ensure_loaded.assert_called_once()


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------

class TestGetById(unittest.TestCase):

    def test_returns_matching_rows_across_categories(self):
        repo = make_repo(data={
            "leads":    [{"ID": "1", "Status": "New"}, {"ID": "2", "Status": "Closed"}],
            "contacts": [{"ID": "1", "Name": "Alice"}, {"ID": "2", "Name": "Bob"}],
        })
        result = repo.get_by_id("1")
        self.assertEqual(result["leads"],    [{"ID": "1", "Status": "New"}])
        self.assertEqual(result["contacts"], [{"ID": "1", "Name": "Alice"}])

    def test_returns_empty_lists_for_no_match(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Status": "New"}],
        })
        result = repo.get_by_id("999")
        self.assertEqual(result["leads"], [])

    def test_all_categories_present_even_without_match(self):
        repo = make_repo(data={
            "leads":    [{"ID": "1"}],
            "contacts": [{"ID": "2"}],
        })
        result = repo.get_by_id("1")
        self.assertIn("leads", result)
        self.assertIn("contacts", result)
        self.assertEqual(result["contacts"], [])

    def test_empty_data_returns_empty_dict(self):
        repo = make_repo(data={})
        result = repo.get_by_id("1")
        self.assertEqual(result, {})

    def test_id_matching_is_exact(self):
        repo = make_repo(data={
            "leads": [{"ID": "12"}, {"ID": "123"}],
        })
        result = repo.get_by_id("12")
        self.assertEqual(len(result["leads"]), 1)
        self.assertEqual(result["leads"][0]["ID"], "12")

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": []})
        repo.ensure_loaded = MagicMock()
        repo.get_by_id("1")
        repo.ensure_loaded.assert_called_once()


# ---------------------------------------------------------------------------
# get_category
# ---------------------------------------------------------------------------

class TestGetCategory(unittest.TestCase):

    def test_returns_full_category(self):
        data = [{"ID": "1", "Status": "New"}, {"ID": "2", "Status": "Closed"}]
        repo = make_repo(data={"leads": data})
        self.assertEqual(repo.get_category("leads"), data)

    def test_returns_empty_list_for_empty_category(self):
        repo = make_repo(data={"leads": []})
        self.assertEqual(repo.get_category("leads"), [])

    def test_raises_for_missing_category(self):
        repo = make_repo(data={})
        with self.assertRaises(KeyError):
            repo.get_category("nonexistent")

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": []})
        repo.ensure_loaded = MagicMock()
        repo.get_category("leads")
        repo.ensure_loaded.assert_called_once()


# ---------------------------------------------------------------------------
# get_by_key
# ---------------------------------------------------------------------------

class TestGetByKey(unittest.TestCase):

    def test_returns_matching_rows(self):
        repo = make_repo(data={
            "leads": [
                {"ID": "1", "Source": "LinkedIn"},
                {"ID": "2", "Source": "Referral"},
            ]
        })
        result = repo.get_by_company("LinkedIn", "Source")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ID"], "1")

    def test_case_insensitive_match(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Source": "LinkedIn"}]
        })
        result = repo.get_by_company("linkedin", "Source")
        self.assertEqual(len(result), 1)

    def test_returns_empty_list_for_no_match(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Source": "LinkedIn"}]
        })
        result = repo.get_by_company("Cold Email", "Source")
        self.assertEqual(result, [])

    def test_searches_across_all_categories(self):
        repo = make_repo(data={
            "leads":    [{"ID": "1", "Source": "LinkedIn"}],
            "contacts": [{"ID": "1", "Source": "LinkedIn"}],
        })
        result = repo.get_by_company("LinkedIn", "Source")
        self.assertEqual(len(result), 2)

    def test_missing_key_in_row_does_not_error(self):
        repo = make_repo(data={
            "leads": [{"ID": "1"}, {"ID": "2", "Source": "LinkedIn"}]
        })
        result = repo.get_by_company("LinkedIn", "Source")
        self.assertEqual(len(result), 1)

    def test_returns_empty_list_for_empty_data(self):
        repo = make_repo(data={"leads": []})
        result = repo.get_by_company("LinkedIn", "Source")
        self.assertEqual(result, [])

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": []})
        repo.ensure_loaded = MagicMock()
        repo.get_by_company("LinkedIn", "Source")
        repo.ensure_loaded.assert_called_once()


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

class TestAdd(unittest.TestCase):

    def test_appends_record_to_category(self):
        repo = make_repo(data={"leads": []})
        repo.add("leads", {"ID": "1", "Status": "New"})
        self.assertEqual(len(repo.data["leads"]), 1)

    def test_record_is_correct(self):
        repo = make_repo(data={"leads": []})
        record = {"ID": "1", "Status": "New"}
        repo.add("leads", record)
        self.assertEqual(repo.data["leads"][0], record)

    def test_multiple_records_appended(self):
        repo = make_repo(data={"leads": []})
        repo.add("leads", {"ID": "1"})
        repo.add("leads", {"ID": "2"})
        self.assertEqual(len(repo.data["leads"]), 2)

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": []})
        repo.ensure_loaded = MagicMock()
        repo.add("leads", {"ID": "1"})
        repo.ensure_loaded.assert_called_once()


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------

class TestSave(unittest.TestCase):

    def test_calls_save_files_with_correct_args(self):
        rows = [{"ID": "1", "Status": "New", "Source": "LinkedIn"}]
        repo = make_repo(data={"leads": rows})
        repo.save("leads")
        repo.handler.save_files.assert_called_once_with(
            "leads.csv", rows, ["ID", "Status", "Source"]
        )

    def test_filename_is_category_plus_csv(self):
        repo = make_repo(data={"contacts": [{"ID": "1", "Name": "Alice", "Role": "CEO"}]})
        repo.save("contacts")
        args = repo.handler.save_files.call_args[0]
        self.assertEqual(args[0], "contacts.csv")

    def test_empty_category_does_not_crash(self):
        repo = make_repo(data={"leads": []})
        try:
            repo.save("leads")
        except Exception as e:
            self.fail(f"save raised unexpectedly: {e}")


# ---------------------------------------------------------------------------
# remove_lead
# ---------------------------------------------------------------------------

class TestRemoveLead(unittest.TestCase):

    def test_removes_matching_row_from_all_categories(self):
        repo = make_repo(data={
            "leads":    [{"ID": "1"}, {"ID": "2"}],
            "contacts": [{"ID": "1"}, {"ID": "2"}],
        })
        repo.save = MagicMock()
        repo.remove_lead("1")
        self.assertEqual(repo.data["leads"],    [{"ID": "2"}])
        self.assertEqual(repo.data["contacts"], [{"ID": "2"}])

    def test_no_match_leaves_data_unchanged(self):
        original = [{"ID": "1"}, {"ID": "2"}]
        repo = make_repo(data={"leads": original.copy()})
        repo.save = MagicMock()
        repo.remove_lead("999")
        self.assertEqual(repo.data["leads"], original)

    def test_save_called_for_each_category(self):
        repo = make_repo(data={
            "leads":    [{"ID": "1"}],
            "contacts": [{"ID": "1"}],
        })
        repo.save = MagicMock()
        repo.remove_lead("1")
        self.assertEqual(repo.save.call_count, 2)

    def test_removes_only_matching_id(self):
        repo = make_repo(data={
            "leads": [{"ID": "1"}, {"ID": "12"}, {"ID": "2"}],
        })
        repo.save = MagicMock()
        repo.remove_lead("1")
        ids = [r["ID"] for r in repo.data["leads"]]
        self.assertNotIn("1", ids)
        self.assertIn("12", ids)
        self.assertIn("2", ids)

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": []})
        repo.ensure_loaded = MagicMock()
        repo.save = MagicMock()
        repo.remove_lead("1")
        repo.ensure_loaded.assert_called_once()

    def test_empty_data_does_not_crash(self):
        repo = make_repo(data={"leads": []})
        repo.save = MagicMock()
        try:
            repo.remove_lead("1")
        except Exception as e:
            self.fail(f"remove_lead raised unexpectedly: {e}")


# ---------------------------------------------------------------------------
# modify_lead
# ---------------------------------------------------------------------------

class TestModifyLead(unittest.TestCase):

    def test_modifies_correct_field(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Status": "New"}]
        })
        repo.save = MagicMock()
        repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_only_modifies_matching_id(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Status": "New"}, {"ID": "2", "Status": "New"}]
        })
        repo.save = MagicMock()
        repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][1]["Status"], "New")

    def test_save_called_after_modify(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Status": "New"}]
        })
        repo.save = MagicMock()
        repo.modify_lead("1", "leads", "Status", "Closed")
        repo.save.assert_called_once_with("leads")

    def test_no_match_does_not_modify(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Status": "New"}]
        })
        repo.save = MagicMock()
        repo.modify_lead("999", "leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "New")

    def test_no_match_does_not_save(self):
        repo = make_repo(data={
            "leads": [{"ID": "1", "Status": "New"}]
        })
        repo.save = MagicMock()
        repo.modify_lead("999", "leads", "Status", "Closed")
        repo.save.assert_not_called()

    def test_invalid_category_raises_key_error(self):
        repo = make_repo(data={"leads": []})
        repo.save = MagicMock()
        with self.assertRaises(KeyError):
            repo.modify_lead("1", "nonexistent", "Status", "Closed")

    def test_calls_ensure_loaded(self):
        repo = make_repo(data={"leads": [{"ID": "1", "Status": "New"}]})
        repo.ensure_loaded = MagicMock()
        repo.save = MagicMock()
        repo.modify_lead("1", "leads", "Status", "Closed")
        repo.ensure_loaded.assert_called_once()


# ---------------------------------------------------------------------------
# create_new_lead
# ---------------------------------------------------------------------------

class TestCreateNewLead(unittest.TestCase):

    def _repo_with_data(self):
        repo = make_repo(data={
            "leads":        [{"ID": "1", "Status": "New", "Source": "LinkedIn"}],
            "contacts":     [{"ID": "1", "Name": "Alice", "Role": "CEO"}],
            "companies":    [{"ID": "1", "Name": "Acme", "Industry": "Tech"}],
            "interactions": [{"ID": "1", "Date": "2024-01-01", "Notes": "First call"}],
        })
        repo.save = MagicMock()
        return repo

    def test_returns_new_id(self):
        repo = self._repo_with_data()
        lead_id = repo.create_new_lead()
        self.assertIsNotNone(lead_id)

    def test_new_record_added_to_all_categories(self):
        repo = self._repo_with_data()
        repo.create_new_lead()
        for category in repo.data:
            self.assertEqual(len(repo.data[category]), 2)

    def test_new_record_has_empty_string_values(self):
        repo = self._repo_with_data()
        lead_id = repo.create_new_lead()
        new_lead = next(r for r in repo.data["leads"] if r["ID"] == lead_id)
        for key, val in new_lead.items():
            if key != "ID":
                self.assertEqual(val, "")

    def test_new_record_id_matches_across_categories(self):
        repo = self._repo_with_data()
        lead_id = repo.create_new_lead()
        for category in repo.data:
            ids = [r["ID"] for r in repo.data[category]]
            self.assertIn(lead_id, ids)

    def test_save_called_for_each_category(self):
        repo = self._repo_with_data()
        repo.create_new_lead()
        self.assertEqual(repo.save.call_count, 4)

    def test_calls_ensure_loaded(self):
        repo = self._repo_with_data()
        repo.ensure_loaded = MagicMock()
        repo.create_new_lead()
        repo.ensure_loaded.assert_called_once()

    def test_creates_lead_on_empty_database(self):
        repo = make_repo(data={
            "leads":        [],
            "contacts":     [],
            "companies":    [],
            "interactions": [],
        })
        repo.save = MagicMock()
        lead_id = repo.create_new_lead()
        self.assertIsNotNone(lead_id)
        self.assertEqual(len(repo.data["leads"]), 1)


if __name__ == "__main__":
    unittest.main()