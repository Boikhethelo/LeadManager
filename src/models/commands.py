from database import manager

class Commands:

    @staticmethod
    def search(user_input : str , key : str) -> None:

        if key.lower().strip() == "id":
            manager.LeadManager.search_by_id(user_input)

