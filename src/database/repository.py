from abc import ABC, abstractmethod
import secrets

class LeadRepository(ABC):
    """
    Abstract class that defines the methods for each type of file repository
    """

    def generate_id(self) -> str:
        """
        returns a unique four character id for each new lead

        """
        return secrets.token_hex(2).upper()


    @abstractmethod
    def get_all(self, category:str) -> list[dict]: ...
    """
    Returns the entire database in memory 
    """


    @abstractmethod
    def get_by_id(self,lead_id: str) -> list[dict]: ...
    """
    Takes the id as a key and returns all data associated with that key
    """

    @abstractmethod
    def get_category(self, key: str) -> list[dict]:...
    """
    get an entire category 
    """

    @abstractmethod
    def get_by_company(self, name: str) -> list[dict]:...
    """
    Use the value and key to partial search and return a list of matches.
    
    """

    @abstractmethod
    def add(self, category: str, record: dict) -> None: ...
    """
    Adds a new lead to the database in memory
    """

    @abstractmethod
    def save(self , category: str) -> None:...

    @abstractmethod
    def remove_lead(self, lead_id:str) -> None:...

    @abstractmethod
    def modify_lead(self, lead_id: str , category: str , key : str ,change : str):...

    @abstractmethod
    def create_new_lead(self) -> str:...







    