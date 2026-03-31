from csv import DictReader
import csv
import configparser
import ast
import os


class LeadData:
    def __init__(self:object):
        self.path = "src/files/"
        self.data = {}
    
    def create_csv_files(self:object) -> None:
        config = configparser.ConfigParser()
        config.read("src/database/config.ini")


        for file in config["Files"]:
            filename = file.lower().strip()
            header_name = filename.removesuffix(".csv")

            if os.path.exists(f"{self.path}{filename}"):
                self.data[header_name] = self.add_data(filename)

            else:
                

                if header_name in config["Fields"]:
                    header = ast.literal_eval(config["Fields"][header_name])
                    self.write_csv_data(filename,header)
                    self.data[header_name] = self.add_data(filename)
                    
    
    def write_csv_data(self:object , file_name:str , header:list[str]) -> None:

        with open(f"{self.path}{file_name}", "w" , newline="" ) as file:
            writer = csv.DictWriter(file , fieldnames=header)

            writer.writeheader()
        

        return None
            
    
    def add_data(self:object, csv_file: str) -> list[dict]:
        """
        Loads csv file and adds the dictionary to the data list

        """
        with open(f"{self.path}{csv_file}" , 'r') as file:
            dict_reader = DictReader(file)
            data = list(dict_reader)
            return data