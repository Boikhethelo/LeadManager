from csv import DictReader
import csv
import configparser
import ast


class LeadData:
    def __init__(self:object):
        
        self.leads = self.get_data("leads.csv") #Needs loads leads from csv to dictionary to be used in app
        self.companies = self.get_data("companies.csv")
        self.interactions = self.get_data("interactions.csv")
        self.calls = self.get_data("calls.csv")
        self.contacts = self.get_data("contacts.csv")
    
    def create_csv_files(self:object) -> None:
        config = configparser.ConfigParser()
        config.read("config.ini")

        companies_header = ast.literal_eval(config["Fields"]["companies"])
        contacts_header = ast.literal_eval(config["Fields"]["contacts"])
        interactions_header = ast.literal_eval(config["Fields"]["interactions"])
        leads_header = ast.literal_eval(config["Fields"]["leads"])
        calls_header = ast.literal_eval(config["Fields"]["calls"])

        file_headers_map = {
        "companies.csv": companies_header,
        "contacts.csv": contacts_header,
        "interactions.csv": interactions_header,
        "leads.csv": leads_header,
        "calls.csv": calls_header
                }

        for file in config["Files"]:
            filename = file.lower().strip()
            header_name = filename.removesuffix(".csv")
            
            if header_name in config["Fields"]:
                header = ast.literal_eval(config["Fields"][header_name])
                self.write_csv_data(filename,header)

    
    def write_csv_data(self:object , file_name:str , header:list[str]) -> None:

        with open(file_name, "w" , newLine="" ) as file:
            writer = csv.DictWriter(file , fieldnames=header)

            writer.writeheader()
        

        return None
            
    
    def get_data(self:object, csv_file: str) -> dict:
        """
        Loads csv file and stores it as a dictionary

        """
        with open(csv_file , 'r') as file:
            dict_reader = DictReader(file)
            data = list(dict_reader)
            return data