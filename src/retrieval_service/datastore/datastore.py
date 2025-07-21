from abc import ABC, abstractmethod
from typing import Generic, TypeVar

class AbstractConfig(ABC):
    kind: str

C = TypeVar("C", bound=AbstractConfig)

class classproperty:
    def __init__(self, func):
        self.fget = func
    def __get__(self, instance, owner):
        return self.fget(owner)

class Client(ABC, Generic[C]):
    @classproperty
    @abstractmethod
    def kind(cls):
        pass

    @abstractmethod
    async def initialize_data(self, paper_chunks: list[dict]) -> None:
        pass

    @abstractmethod
    async def search_documents(
        self, query_embedding: list[float], top_k: int
    ) -> list[dict]:
        raise NotImplementedError("Subclass should implement this!")

    @abstractmethod
    async def add_documents(self, paper_chunks: list[dict]) -> None:
        pass