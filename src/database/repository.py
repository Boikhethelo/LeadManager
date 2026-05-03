from abc import ABC, abstractmethod
import uuid

class LeadRepository(ABC):
    """
    Abstract class that defines the methods for each type of file repository
    """

    def generate_id(self) -> str:
        return str(uuid.uuid4())


    @abstractmethod
    def get_all(self, category:str) -> list[dict]: ...
    """
    Returns the entire database in memory 
    """


    @abstractmethod
    def get_by_id(self,lead_id: str) -> dict: ...
    """
    Takes the id as a key and returns all data associated with that key
    """

    @abstractmethod
    def get_category(self, key: str) -> list[dict]:...
    """
    get an entire category 
    """

    @abstractmethod
    def get_by_key(self, value: str , key: str) -> dict:...
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







    