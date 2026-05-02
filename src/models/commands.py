from database.repository import LeadRepository

class Commands:
    def __init__(self, repository: LeadRepository):
        self.repository = repository

    

    def search(self,user_input : str , key : str) -> list[dict] | dict | None:

        if key.lower().strip() == "id":
            return self.repository.get_by_id(user_input)

        elif key.lower().strip() == "category":
            return self.repository.get_category(user_input)

        else:
            return self.repository.get_by_key(user_input,key)

