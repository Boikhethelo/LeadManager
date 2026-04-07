from database import creator , manager

class Commands:
    def __init__(self):
        self.config = creator.LeadConfig()
        self.handler = creator.LeadFileHandler()
        self.lead_manager = manager.LeadManager(self.handler, self.config)
    

    def search(self,user_input : str , key : str) -> None:

        if key.lower().strip() == "id":
            self.lead_manager.initialize_system()
            return self.lead_manager.search_by_id(user_input)

