import csv
import unittest
from pathlib import Path
import tempfile
import os

from src.database.creator import LeadFileHandler  # adjust import path as needed


class TestLeadFileHandlerInit(unittest.TestCase):

    def test_default_directory_is_set(self):
        """Default directory should resolve to a Path ending in 'files'."""
        handler = LeadFileHandler()
        self.assertIsInstance(handler.directory, Path)
        self.assertEqual(handler.directory.name, "files")

    def test_custom_directory_is_set(self):
        """A custom directory passed in should be stored as a Path."""
        handler = LeadFileHandler(directory="/tmp/custom")
        self.assertEqual(handler.directory, Path("/tmp/custom"))

    def test_string_directory_is_converted_to_path(self):
        """A string directory should be converted to a Path object."""
        handler = LeadFileHandler(directory="/tmp/leads")
        self.assertIsInstance(handler.directory, Path)


class TestLeadFileHandlerReadFile(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.handler = LeadFileHandler(directory=self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _write_csv(self, filename: str, rows: list[dict], fieldnames: list[str]):
        filepath = os.path.join(self.tmp_dir.name, filename)
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_returns_list(self):
        """read_file should return a list."""
        self._write_csv("test.csv", [], fieldnames=["ID", "Name"])
        result = self.handler.read_file("test.csv")
        self.assertIsInstance(result, list)

    def test_reads_rows_correctly(self):
        """read_file should return all rows as dicts."""
        rows = [{"ID": "1", "Name": "Alice"}, {"ID": "2", "Name": "Bob"}]
        self._write_csv("contacts.csv", rows, fieldnames=["ID", "Name"])
        result = self.handler.read_file("contacts.csv")
        self.assertEqual(result, rows)

    def test_empty_file_returns_empty_list(self):
        """A CSV with only a header should return an empty list."""
        self._write_csv("empty.csv", [], fieldnames=["ID", "Name"])
        result = self.handler.read_file("empty.csv")
        self.assertEqual(result, [])

    def test_returns_list_of_dicts(self):
        """Each row returned should be a dict."""
        rows = [{"ID": "1", "Name": "Alice"}]
        self._write_csv("contacts.csv", rows, fieldnames=["ID", "Name"])
        result = self.handler.read_file("contacts.csv")
        self.assertIsInstance(result[0], dict)

    def test_keys_match_header(self):
        """Dict keys in returned rows should match the CSV header."""
        rows = [{"ID": "1", "Name": "Alice"}]
        self._write_csv("contacts.csv", rows, fieldnames=["ID", "Name"])
        result = self.handler.read_file("contacts.csv")
        self.assertEqual(set(result[0].keys()), {"ID", "Name"})

    def test_single_row(self):
        """read_file should handle a single data row correctly."""
        rows = [{"ID": "99", "Name": "Solo"}]
        self._write_csv("single.csv", rows, fieldnames=["ID", "Name"])
        result = self.handler.read_file("single.csv")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Name"], "Solo")

    def test_file_not_found_raises(self):
        """read_file should raise FileNotFoundError for a missing file."""
        with self.assertRaises(FileNotFoundError):
            self.handler.read_file("nonexistent.csv")

    def test_multiple_columns(self):
        """read_file should correctly parse rows with many columns."""
        fieldnames = ["ID", "Name", "Email", "Phone"]
        rows = [{"ID": "1", "Name": "Alice", "Email": "a@a.com", "Phone": "123"}]
        self._write_csv("multi.csv", rows, fieldnames=fieldnames)
        result = self.handler.read_file("multi.csv")
        self.assertEqual(result[0]["Email"], "a@a.com")
        self.assertEqual(result[0]["Phone"], "123")


class TestLeadFileHandlerWriteFile(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.handler = LeadFileHandler(directory=self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _filepath(self, filename: str) -> str:
        return os.path.join(self.tmp_dir.name, filename)

    def test_file_is_created(self):
        """write_file should create the file on disk."""
        self.handler.write_file("output.csv", ["ID", "Name"])
        self.assertTrue(os.path.exists(self._filepath("output.csv")))

    def test_header_is_written(self):
        """write_file should write the header row to the CSV."""
        self.handler.write_file("output.csv", ["ID", "Name", "Email"])
        with open(self._filepath("output.csv"), "r") as f:
            reader = csv.reader(f)
            header = next(reader)
        self.assertEqual(header, ["ID", "Name", "Email"])

    def test_file_contains_only_header(self):
        """write_file should write only the header — no data rows."""
        self.handler.write_file("output.csv", ["ID", "Name"])
        with open(self._filepath("output.csv"), "r") as f:
            rows = list(csv.reader(f))
        self.assertEqual(len(rows), 1)

    def test_single_column_header(self):
        """write_file should handle a header with a single column."""
        self.handler.write_file("single.csv", ["ID"])
        with open(self._filepath("single.csv"), "r") as f:
            header = next(csv.reader(f))
        self.assertEqual(header, ["ID"])

    def test_overwrites_existing_file(self):
        """write_file should overwrite an existing file cleanly."""
        self.handler.write_file("output.csv", ["ID", "Name"])
        self.handler.write_file("output.csv", ["Code", "Value"])
        with open(self._filepath("output.csv"), "r") as f:
            header = next(csv.reader(f))
        self.assertEqual(header, ["Code", "Value"])

    def test_written_file_is_readable_by_read_file(self):
        """A file created by write_file should be readable by read_file without errors."""
        self.handler.write_file("roundtrip.csv", ["ID", "Name"])
        result = self.handler.read_file("roundtrip.csv")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()