from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.documents import Document

class VectorStoreRepository(ABC):
    """
    Abstract interface for Vector Store interactions.
    Follows the Repository pattern to isolate the domain from the persistence layer.
    """
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """
        Adds a list of LangChain documents to the store.
        """
        pass

    @abstractmethod
    async def similarity_search(self, query: str, session_id: str, k: int = 4) -> List[Document]:
        """
        Performs a similarity search within a specific session.
        """
        pass

    @abstractmethod
    async def delete_by_session(self, session_id: str) -> None:
        """
        Deletes all documents associated with a session.
        """
        pass
