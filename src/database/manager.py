import os
from database import creator

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



    def search_by_id(self, id: str)  -> list[dict] | None:
        """
        takes a key and an id and returns all data associated with the key and id
        """
        output = []
        for category in self.data.values():
            
            for lead in category:
                if lead.get("ID") == id:
                    output.append(lead)

        return output
    
    