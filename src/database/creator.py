import csv
from csv import DictReader
import configparser
import ast

class LeadFileHandler:

    """
    This class handles the reading and writing of the csv files

    """

    def __init__(self, directory="src/files/"):
        self.directory = directory

    def read_file(self, filename: str) -> list[dict]:
        with open(f"{self.directory}{filename}", 'r') as file:
            return list(DictReader(file))

    def write_file(self, filename: str, header: list[str]) -> None:
        with open(f"{self.directory}{filename}", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()


class LeadConfig:

    """

    This class handles the reading of the config file and storing its parameters.
    
    """
    def __init__(self, config_path="src/database/config.ini"):
        self.path = config_path

    def get_definitions(self) -> list[dict]:
        config = configparser.ConfigParser()
        config.read(self.path)
        
        fields_dict = []
        for file in config["Files"]:
            name = file.lower().strip()
            header_name = name.removesuffix(".csv")
            header = ast.literal_eval(config["Fields"].get(header_name, "[]"))
            fields_dict.append({"filename": name, "header": header, "key": header_name})
            
        return fields_dict
    


    
