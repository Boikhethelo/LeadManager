import os
from database import creator
from pprint import pprint

class LeadManager:
    def __init__(self, handler: creator.LeadFileHandler, config: creator.LeadConfig):
        self.handler = handler
        self.config = config
        self.data = {}

    def initialize_system(self):
        """
        Checks if all files exist if not creates new ones 

        """
        
        for field in self.config.get_definitions():
            full_path = os.path.join(self.handler.directory, field["filename"])
            
            if not os.path.exists(full_path):
                self.handler.write_file(field["filename"], field["header"])
            
            self.data[field["key"]] = self.handler.read_file(field["filename"])



    def search_by_id(self, id: str)  -> dict:
        """
        takes a key and an id and returns all data associated with the key and id
        """
        full_lead = {}
      
        for category in self.data:
            data = []
            full_lead.update({category:data})

            for lead in self.data[category]:

                if lead.get("ID") == id:
                    full_lead[category].append(lead)

            
        return full_lead
    
    