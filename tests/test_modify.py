"""
tests/test_modify_handling.py

Full test suite for the modify layer.  Each group is labelled with the bug
it exposes so you can fix one class of problem at a time.

Layers covered
──────────────
1. CsvLeadRepository.modify_lead  — storage layer
2. Commands.modify                — service layer
3. ModifyHandler.handle           — CLI handler
4. App.parse_modify               — input validation
"""

import argparse
import copy
import unittest
from unittest.mock import MagicMock, patch

from database.csv_repository import CsvLeadRepository
from models.commands import Commands
from models.cli_commands import ModifyHandler


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_handler(directory="/tmp/leads"):
    handler = MagicMock()
    handler.directory = directory
    return handler


def make_config(definitions=None):
    config = MagicMock()
    if definitions is None:
        definitions = [
            {
                "key": "leads",
                "filename": "leads.csv",
                "header": ["ID", "Status", "Source", "Potential Value"],
            },
            {
                "key": "contacts",
                "filename": "contacts.csv",
                "header": ["ID", "Name", "Role"],
            },
        ]
    config.get_definitions.return_value = definitions
    return config


def make_repo(data=None):
    repo = CsvLeadRepository(make_handler(), make_config())
    if data is not None:
        repo.data = data
    repo.save = MagicMock()
    return repo


# Canonical sample — always deep-copy so tests are independent
SAMPLE_DATA = {
    "leads": [
        {"ID": "1", "Status": "New",       "Source": "LinkedIn", "Potential Value": "50000"},
        {"ID": "2", "Status": "Contacted", "Source": "Referral", "Potential Value": "120000"},
    ],
    "contacts": [
        {"ID": "1", "Name": "Alice", "Role": "CEO"},
        {"ID": "2", "Name": "Bob",   "Role": "CTO"},
    ],
}


def fresh():
    return copy.deepcopy(SAMPLE_DATA)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Category case-insensitivity
#    BUG: self.data[category] KeyErrors on "Leads", "LEADS", " leads " etc.
# ─────────────────────────────────────────────────────────────────────────────

class TestCategoryCase(unittest.TestCase):

    def test_lowercase_category(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_titlecase_category(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "Leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_uppercase_category(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "LEADS", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_mixed_case_category(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "LeAdS", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_category_with_surrounding_whitespace(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "  leads  ", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_uppercase_contacts_category(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "CONTACTS", "Name", "Charlie")
        self.assertEqual(repo.data["contacts"][0]["Name"], "Charlie")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Field/key case-insensitivity
#    BUG: lead[key] = change adds "status" alongside existing "Status"
# ─────────────────────────────────────────────────────────────────────────────

class TestFieldCase(unittest.TestCase):

    def test_exact_field_case(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Qualified")
        self.assertEqual(repo.data["leads"][0]["Status"], "Qualified")

    def test_lowercase_field(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "status", "Qualified")
        self.assertEqual(repo.data["leads"][0]["Status"], "Qualified")

    def test_uppercase_field(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "STATUS", "Qualified")
        self.assertEqual(repo.data["leads"][0]["Status"], "Qualified")

    def test_lowercase_field_does_not_add_duplicate_key(self):
        """'status' must update 'Status', not sit alongside it."""
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "status", "Qualified")
        self.assertNotIn("status", repo.data["leads"][0])
        self.assertIn("Status", repo.data["leads"][0])

    def test_uppercase_field_does_not_add_duplicate_key(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "STATUS", "Qualified")
        self.assertNotIn("STATUS", repo.data["leads"][0])

    def test_record_key_count_unchanged_after_modify(self):
        """Successful modify must never change the number of keys in a record."""
        repo = make_repo(fresh())
        original_key_count = len(repo.data["leads"][0])
        repo.modify_lead("1", "leads", "status", "Qualified")
        self.assertEqual(len(repo.data["leads"][0]), original_key_count)

    def test_multiword_field_lowercase(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "potential value", "99999")
        self.assertEqual(repo.data["leads"][0]["Potential Value"], "99999")

    def test_multiword_field_uppercase(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "POTENTIAL VALUE", "99999")
        self.assertEqual(repo.data["leads"][0]["Potential Value"], "99999")

    def test_field_with_surrounding_whitespace(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "  Status  ", "Qualified")
        self.assertEqual(repo.data["leads"][0]["Status"], "Qualified")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Invalid category
#    BUG: raises KeyError — should return a descriptive error string
# ─────────────────────────────────────────────────────────────────────────────

class TestInvalidCategory(unittest.TestCase):

    def test_does_not_raise(self):
        repo = make_repo(fresh())
        try:
            repo.modify_lead("1", "nonexistent", "Status", "Closed")
        except (KeyError, Exception) as exc:
            self.fail(f"modify_lead raised unexpectedly: {exc}")

    def test_returns_error_string(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("1", "nonexistent", "Status", "Closed")
        self.assertIsInstance(result, str)

    def test_error_string_mentions_the_bad_category(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("1", "nonexistent", "Status", "Closed")
        self.assertIn("nonexistent", result.lower())

    def test_data_unchanged(self):
        repo = make_repo(fresh())
        snapshot = copy.deepcopy(repo.data)
        repo.modify_lead("1", "nonexistent", "Status", "Closed")
        self.assertEqual(repo.data, snapshot)

    def test_save_not_called(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "nonexistent", "Status", "Closed")
        repo.save.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Invalid field
#    BUG: lead["bad_field"] = value silently creates a junk key
# ─────────────────────────────────────────────────────────────────────────────

class TestInvalidField(unittest.TestCase):

    def test_returns_error_string(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("1", "leads", "bad_field", "value")
        self.assertIsInstance(result, str)

    def test_junk_key_not_created(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "bad_field", "value")
        self.assertNotIn("bad_field", repo.data["leads"][0])

    def test_existing_values_unchanged(self):
        repo = make_repo(fresh())
        original_status = repo.data["leads"][0]["Status"]
        repo.modify_lead("1", "leads", "bad_field", "value")
        self.assertEqual(repo.data["leads"][0]["Status"], original_status)

    def test_save_not_called(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "bad_field", "value")
        repo.save.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# 5. ID not found
#    BUG: silently returns None — should return a descriptive error string
# ─────────────────────────────────────────────────────────────────────────────

class TestIdNotFound(unittest.TestCase):

    def test_returns_error_string(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("999", "leads", "Status", "Closed")
        self.assertIsInstance(result, str)

    def test_error_string_mentions_the_missing_id(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("999", "leads", "Status", "Closed")
        self.assertIn("999", result)

    def test_data_unchanged(self):
        repo = make_repo(fresh())
        snapshot = copy.deepcopy(repo.data)
        repo.modify_lead("999", "leads", "Status", "Closed")
        self.assertEqual(repo.data, snapshot)

    def test_save_not_called(self):
        repo = make_repo(fresh())
        repo.modify_lead("999", "leads", "Status", "Closed")
        repo.save.assert_not_called()

    def test_empty_category_returns_error_string(self):
        repo = make_repo({"leads": [], "contacts": []})
        result = repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertIsInstance(result, str)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Successful modify — return value + side effects
# ─────────────────────────────────────────────────────────────────────────────

class TestModifySuccess(unittest.TestCase):

    def test_returns_string(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertIsInstance(result, str)

    def test_success_string_mentions_id(self):
        repo = make_repo(fresh())
        result = repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertIn("1", result)

    def test_value_updated_in_memory(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed")

    def test_only_target_record_is_changed(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Closed")
        self.assertEqual(repo.data["leads"][1]["Status"], "Contacted")

    def test_save_called_once_with_correct_category(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Closed")
        repo.save.assert_called_once_with("leads")

    def test_other_category_not_saved(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Closed")
        saved = [c.args[0] for c in repo.save.call_args_list]
        self.assertNotIn("contacts", saved)

    def test_multiword_value_saved_correctly(self):
        repo = make_repo(fresh())
        repo.modify_lead("1", "leads", "Status", "Closed Won")
        self.assertEqual(repo.data["leads"][0]["Status"], "Closed Won")

    def test_ensure_loaded_called(self):
        repo = make_repo(fresh())
        repo.ensure_loaded = MagicMock()
        repo.modify_lead("1", "leads", "Status", "Closed")
        repo.ensure_loaded.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# 7. Commands.modify — delegation and return-value passthrough
# ─────────────────────────────────────────────────────────────────────────────

class TestCommandsModify(unittest.TestCase):

    def _commands(self, return_value="OK"):
        repo = MagicMock()
        repo.modify_lead.return_value = return_value
        return Commands(repo), repo

    def test_delegates_all_args_to_repository(self):
        cmds, repo = self._commands()
        cmds.modify("1", "leads", "Status", "Closed")
        repo.modify_lead.assert_called_once_with("1", "leads", "Status", "Closed")

    def test_passes_through_success_result(self):
        cmds, repo = self._commands(return_value="Lead 1 updated.")
        self.assertEqual(cmds.modify("1", "leads", "Status", "Closed"), "Lead 1 updated.")

    def test_passes_through_error_result(self):
        cmds, repo = self._commands(return_value="Error: ID 999 not found.")
        self.assertEqual(cmds.modify("999", "leads", "Status", "Closed"), "Error: ID 999 not found.")

    def test_multiword_change_passed_unchanged(self):
        cmds, repo = self._commands()
        cmds.modify("1", "leads", "Status", "Closed Won")
        repo.modify_lead.assert_called_once_with("1", "leads", "Status", "Closed Won")


# ─────────────────────────────────────────────────────────────────────────────
# 8. ModifyHandler.handle — display wiring
#    BUG: handler never calls display, result is silently discarded
#    FIX: ModifyHandler.__init__ must accept `display` and handle must call it
# ─────────────────────────────────────────────────────────────────────────────

class TestModifyHandlerDisplay(unittest.TestCase):

    def _handler(self, return_value="Done"):
        commands = MagicMock()
        commands.modify.return_value = return_value
        display = MagicMock()
        # After the fix, ModifyHandler should accept display as a second arg,
        # mirroring SearchHandler and AddLeadHandler
        handler = ModifyHandler(commands, display)
        return handler, commands, display

    def _args(self, id="1", category="leads", key="Status", change="Closed"):
        return argparse.Namespace(id=id, category=category, key=key, change=change)

    def test_calls_commands_modify_with_correct_args(self):
        handler, commands, _ = self._handler()
        handler.handle(self._args())
        commands.modify.assert_called_once_with("1", "leads", "Status", "Closed")

    def test_display_called_with_result(self):
        handler, _, display = self._handler(return_value="Lead 1 updated.")
        handler.handle(self._args())
        display.assert_called_once_with("Lead 1 updated.")

    def test_display_called_with_error_string(self):
        handler, _, display = self._handler(return_value="Error: ID 999 not found.")
        handler.handle(self._args(id="999"))
        display.assert_called_once_with("Error: ID 999 not found.")

    def test_display_called_exactly_once(self):
        handler, _, display = self._handler()
        handler.handle(self._args())
        display.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# 9. App.parse_modify — input validation
# ─────────────────────────────────────────────────────────────────────────────

class TestParseModify(unittest.TestCase):

    def _app(self):
        from app import App
        with patch("app.LeadFileHandler"), \
             patch("app.LeadConfig"), \
             patch("app.CsvLeadRepository"), \
             patch("app.Controller"):
            return App()

    def test_only_command_returns_none(self):
        app = self._app()
        self.assertIsNone(app.parse_modify(["modify"]))

    def test_missing_field_returns_none(self):
        app = self._app()
        self.assertIsNone(app.parse_modify(["modify", "1", "leads"]))

    def test_missing_value_returns_none(self):
        app = self._app()
        self.assertIsNone(app.parse_modify(["modify", "1", "leads", "Status"]))

    def test_five_parts_returns_list(self):
        app = self._app()
        result = app.parse_modify(["modify", "1", "leads", "Status", "Closed"])
        self.assertIsNotNone(result)

    def test_returns_correct_five_element_structure(self):
        app = self._app()
        result = app.parse_modify(["modify", "42", "contacts", "Role", "Director"])
        self.assertEqual(result, ["modify", "42", "contacts", "Role", "Director"])

    def test_multiword_value_is_joined(self):
        app = self._app()
        result = app.parse_modify(["modify", "1", "leads", "Status", "Closed", "Won"])
        self.assertEqual(result[4], "Closed Won")

    def test_three_word_value_fully_joined(self):
        app = self._app()
        result = app.parse_modify(["modify", "1", "leads", "Source", "Cold", "Email", "Campaign"])
        self.assertEqual(result[4], "Cold Email Campaign")

    def test_output_always_has_exactly_five_elements(self):
        """Value tokens are always collapsed into index 4, so len is always 5."""
        app = self._app()
        result = app.parse_modify(["modify", "1", "leads", "Status", "A", "B", "C"])
        self.assertEqual(len(result), 5)


if __name__ == "__main__":
    unittest.main()