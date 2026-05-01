from abc import ABC, abstractmethod



class LeadRepository(ABC):

    @abstractmethod
    def get_all(self, category:str) -> list[dict]: ...


    @abstractmethod
    def get_by_id(self,category: str, id: str) -> list[dict]: ...


    @abstractmethod
    def add(self, category: str, record: dict) -> None: ...






    