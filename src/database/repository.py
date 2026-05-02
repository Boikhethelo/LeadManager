from abc import ABC, abstractmethod

class LeadRepository(ABC):
    """
    Abstract class that defines the methods for each type of file repository
    """

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

    @abstractmethod
    def get_by_key(self, value: str , key: str) -> dict:...



    @abstractmethod
    def add(self, category: str, record: dict) -> None: ...
    """
    Adds a new lead to the database in memory
    """






    