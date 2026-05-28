import os
import csv
import configparser
import ast
from csv import DictReader
from pathlib import Path


from database.repository import LeadRepository

BASE_DIR = Path(__file__).resolve().parent



class LeadConfig:
     """

     This class handles the reading of the config file and storing its parameters.

     """

     def __init__(self, config_path: Path = BASE_DIR / "config.ini"):
         self.path = Path(config_path)

     def get_definitions(self) -> list[dict]:
         config = configparser.ConfigParser()
         config.read(self.path)

         fields_dict = []
         for file in config["Files"]:
             name = config["Files"][file]
             header_name = name.removesuffix(".csv")
             header = ast.literal_eval(config["Fields"].get(header_name, "[]"))
             fields_dict.append({"filename": name, "header": header, "key": header_name})

         return fields_dict




class LeadFileHandler:

    """
    This class handles the reading and writing of the csv files

    """

    def __init__(self, directory: Path = BASE_DIR.parent/"files"):
        self.directory = Path(directory)

    def read_file(self, filename: str) -> list[dict]:
        with open(f"{self.directory}/{filename}", 'r') as file:
            return list(DictReader(file))

    def write_file(self, filename: str, header: list[str]) -> None:
        with open(f"{self.directory}/{filename}", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()

    def save_files(self, filename: str, rows: list[dict] , header: list[str]) -> None:
        with open(f"{self.directory}/{filename}" , "w" , newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)



class CsvLeadRepository(LeadRepository):
    """
    A class to handled the data from the csv files stored in memory
    
    """
    def __init__(self, handler:LeadFileHandler, config:LeadConfig):
        self.handler = handler
        self.config = config
        self.data = {}

    def ensure_loaded(self):
        """
        Checks if all files exist if not creates new ones 

        """
        if self.data:
            return
        
        for field in self.config.get_definitions():
            full_path = os.path.join(self.handler.directory, field["filename"])
            
            if not os.path.exists(full_path):
                self.handler.write_file(field["filename"], field["header"])
            
            self.data[field["key"]] = self.handler.read_file(field["filename"])


    def get_all(self, category: str) -> list[dict]:
        """
        Return the entire lead database in memory

        """
        self.ensure_loaded()
        return self.data.get(category, [])



    def get_by_id(self, lead_id: str)  -> dict:
        """
        takes a key and an id and returns all data associated with the key and id
        """
        self.ensure_loaded()
        full_lead = {}
      
        for category in self.data:
            data = []
            full_lead.update({category:data})

            for lead in self.data[category]:

                if lead.get("ID") == lead_id:
                    full_lead[category].append(lead)

        return full_lead

    def get_category(self, key: str) -> list[dict]:

        self.ensure_loaded()

        return self.data[key]

    def get_by_key(self, value: str , key: str) -> list[dict]:

        self.ensure_loaded()
        matches = []

        for category in self.data:
                for lead in self.data[category]:
                    if lead.get(key, "").lower() == value.lower(): #Partial matching
                        matches.append(lead)
        return matches



    def add(self, category: str , record: dict):
        self.ensure_loaded()
        self.data[category].append(record)


    def save(self, category) -> None:
        filename = f"{category}.csv"
        definitions = {f["key"]: f for f in self.config.get_definitions()}
        header = definitions[category]["header"]
        self.handler.save_files(filename,self.data[category],header)

    def remove_lead(self, lead_id:str):

        self.ensure_loaded()

        for category in self.data:
            self.data[category] = [lead for lead in self.data[category] if lead.get("ID") != lead_id]
            self.save(category)

    def modify_lead(self, lead_id: str , category: str, key: str , change : str):

        self.ensure_loaded()

        for lead in self.data[category]:

            if lead.get("ID") == lead_id:
                lead[key] = change
                self.save(category)
                return
            else:
                pass

    def create_new_lead(self):

        self.ensure_loaded()
        lead_id = self.generate_id()


        for field in self.config.get_definitions():
            category = field["key"]
            record = {"ID" : lead_id}
            for key in field["header"]:
                if key != "ID":
                    record[key] = ""
            self.data[category].append(record)
            self.save(category)

        return lead_id









    





        
    
    