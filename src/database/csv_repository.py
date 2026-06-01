"""
repository.py

Provides core file handling and data repository functionality for the Lead Manager tool.
Handles importing, exporting, and managing company and contact records via CSV storage.
"""
import os
import csv
import configparser
import ast
from csv import DictReader
from pathlib import Path
from database.repository import LeadRepository

BASE_DIR = Path(__file__).resolve().parent

class LeadConfig:
    """Handles the reading of the configuration file and parsing file definitions.

    Attributes:
        path (Path): The absolute path to the configuration file (default: config.ini).
    """

    def __init__(self, config_path: Path = BASE_DIR / "config.ini"):
        self.path = Path(config_path)

    def get_definitions(self) -> list[dict]:
        """Reads the config file and constructs dictionaries for each CSV file definition.

        Returns:
            list[dict]: A list containing configuration dictionaries for each file.
                        Each dict contains 'filename', 'header' (list of fields), and 'key'.
        """
        config = configparser.ConfigParser()
        config.read(self.path)

        fields_dict = []
        for file in config["Files"]:
            name = config["Files"][file]
            header_name = name.removesuffix(".csv")

            # Safely evaluate the string representation of the list from the config
            header = ast.literal_eval(config["Fields"].get(header_name, "[]"))
            fields_dict.append({"filename": name, "header": header, "key": header_name})

        return fields_dict

class LeadFileHandler:
    """Handles the low-level reading and writing of CSV files.

    Attributes:
        directory (Path): The directory path where the CSV files are stored.
    """

    def __init__(self, directory: Path = BASE_DIR.parent / "files"):
        self.directory = Path(directory)

    def read_file(self, filename: str) -> list[dict]:
        """Reads a CSV file and returns its contents.

        Args:
            filename (str): The name of the CSV file to read.

        Returns:
            list[dict]: A list of dictionaries representing the rows in the CSV file.
        """
        with open(f"{self.directory}/{filename}", 'r') as file:
            return list(DictReader(file))

    def write_file(self, filename: str, header: list[str]) -> None:
        """Creates a new CSV file and writes the header row.

        Args:
            filename (str): The name of the new CSV file.
            header (list[str]): A list of column names for the header.
        """
        with open(f"{self.directory}/{filename}", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()

    def save_files(self, filename: str, rows: list[dict], header: list[str]) -> None:
        """Overwrites an existing CSV file with new data.

        Args:
            filename (str): The name of the CSV file to save.
            rows (list[dict]): The complete list of data rows to write.
            header (list[str]): The column headers for the file.
        """
        with open(f"{self.directory}/{filename}", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

class CsvLeadRepository(LeadRepository):
    """Manages lead data loaded into memory from CSV files.

    Acts as the primary interface for creating, reading, updating, and deleting leads.

    Attributes:
        handler (LeadFileHandler): The file handler instance for disk operations.
        config (LeadConfig): The configuration instance for file definitions.
        data (dict): The in-memory storage of all loaded CSV data.
    """

    def __init__(self, handler: LeadFileHandler, config: LeadConfig):
        self.handler = handler
        self.config = config
        self.data = {}

    def ensure_loaded(self) -> None:
        """Checks if files are loaded in memory. If not, initializes or loads them.

        This prevents redundant disk reads on subsequent operations.
        """
        if self.data:
            return

        for field in self.config.get_definitions():
            full_path = os.path.join(self.handler.directory, field["filename"])

            if not os.path.exists(full_path):
                self.handler.write_file(field["filename"], field["header"])

            self.data[field["key"]] = self.handler.read_file(field["filename"])

    def get_all(self, category: str) -> list[dict]:
        """Retrieves the entire lead dataset for a specific category.

        Args:
            category (str): The data category to retrieve (e.g., 'company', 'leads').

        Returns:
            list[dict]: A list of all records within the specified category.
        """
        self.ensure_loaded()
        return self.data.get(category, [])

    def get_by_id(self, lead_id: str) -> list[dict]:
        """Fetches all data associated with a specific lead ID across all categories.

        Args:
            lead_id (str): The unique identifier for the lead.

        Returns:
            list[dict]: A structured list containing the aggregated data for the lead.
        """
        self.ensure_loaded()
        full_lead = {}
        output = []

        # Aggregate data from all categories (e.g., company, contact info) for this specific ID
        for category in self.data:
            data = []
            full_lead.update({category: data})

            for lead in self.data[category]:
                if lead.get("ID") == lead_id:
                    full_lead[category].append(lead)

        output.append(full_lead)
        return output

    def get_category(self, key: str) -> list[dict]:
        """Fetches all records for a given configuration key."""
        self.ensure_loaded()
        return self.data[key]

    def get_by_company(self, name: str) -> list[dict]:
        """Searches for leads matching a specific company name.

        Args:
            name (str): The company name to search for.

        Returns:
            list[dict]: A list of full lead profiles matching the company name.
        """
        self.ensure_loaded()
        matches = []

        for lead in self.data["company"]:
            # Utilize partial matching and case-insensitivity for broader search results
            if name in lead.get("Name", "").lower():
                full_lead = self.get_by_id(lead.get("ID"))
                matches.append(full_lead[0])

        return matches

    def add(self, category: str, record: dict) -> None:
        """Adds a new record to the specified category in memory.

        Args:
            category (str): The data category to append to.
            record (dict): The dictionary containing the new record data.
        """
        self.ensure_loaded()
        self.data[category].append(record)

    def save(self, category: str) -> None:
        """Saves a specific category's in-memory data back to its respective CSV file.

        Args:
            category (str): The category key defining which file to update.
        """
        filename = f"{category}.csv"
        definitions = {f["key"]: f for f in self.config.get_definitions()}
        header = definitions[category]["header"]

        self.handler.save_files(filename, self.data[category], header)

    def remove_lead(self, lead_id: str) -> str:
        """Deletes a lead from all categories and updates the CSV files.

        Args:
            lead_id (str): The unique identifier of the lead to remove.

        Returns:
            str: A confirmation message indicating the lead was removed.
        """
        self.ensure_loaded()

        # Rebuild the dataset excluding the specified ID across all categories
        for category in self.data:
            self.data[category] = [lead for lead in self.data[category] if lead.get("ID") != lead_id]
            self.save(category)

        return f"lead: {lead_id} has been removed."

    def modify_lead(self, lead_id: str, category: str, key: str, change: str) -> str:
        """Updates a specific field for an existing lead.

        Args:
            lead_id (str): The unique identifier of the lead.
            category (str): The category where the change should occur.
            key (str): The specific field/column to update.
            change (str): The new value to set.

        Returns:
            str: A status message indicating success or failure.
        """
        self.ensure_loaded()

        for lead in self.data[category]:
            if lead.get("ID") == lead_id:
                lead[key] = change
                self.save(category)
                return f"lead: {lead_id} {category} updated to {change}"

        return f"Unable to locate lead {lead_id}"

    def create_new_lead(self) -> str:
        """Generates a new unique lead with empty fields across all configuration categories.

        Returns:
            str: A confirmation message containing the new lead ID.
        """
        self.ensure_loaded()
        existing_ids = {row["ID"] for row in self.data.get("leads", [])}

        lead_id = self.generate_id()

        # Ensure the generated ID is truly unique
        while lead_id in existing_ids:
            lead_id = self.generate_id()

        # Scaffold empty data for the new lead based on configuration fields
        for field in self.config.get_definitions():
            category = field["key"]
            record = {"ID": lead_id}

            for key in field["header"]:
                if key != "ID":
                    record[key] = ""

            self.data[category].append(record)
            self.save(category)

        return f"New lead created with id of : {lead_id}"









    





        
    
    