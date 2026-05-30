from database.repository import LeadRepository

class Commands:
    def __init__(self, repository: LeadRepository):
        self.repository = repository

    

    def search(self,user_input : str , key : str) -> list[dict] | dict | None:

        if key.lower().strip() == "id":
            return self.repository.get_by_id(user_input)
        elif key.lower().strip() == "company":
            return self.repository.get_by_company(user_input)

        elif key.lower().strip() == "category":
            return self.repository.get_category(user_input)

        else:
           print("Unknown search call")

    def delete(self, lead_id : str) -> None:
        return self.repository.remove_lead(lead_id)


    def modify(self,id : str , category: str , key: str ,change : str):
        return self.repository.modify_lead(id, category , key ,change)

    def add_new_lead(self):
        return self.repository.create_new_lead()



