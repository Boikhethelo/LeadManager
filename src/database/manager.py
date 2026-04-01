import os
from creator import LeadFileHandler , LeadConfig

class LeadManager:
    def __init__(self, handler: LeadFileHandler, config: LeadConfig):
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



    def search_by_id(self, lead_id: str) -> dict | None:
        "FIX"
        for category in self.data.values():
            
            for lead in category:
                if lead.get("id") == lead_id:
                    return lead
        return None