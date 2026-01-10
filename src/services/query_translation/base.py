from abc import ABC, abstractmethod
from typing import List
from enum import Enum

class QueryTranslationType(Enum):
    """Enum for supported query translation techniques."""
    IDENTITY = "identity"
    MULTI_QUERY = "multi_query"
    HYDE = "hyde"
    DECOMPOSITION = "decomposition"
    STEP_BACK = "step_back"

class BaseQueryTranslator(ABC):
    """Abstract base class for query translation techniques."""
    
    @abstractmethod
    async def translate(self, query: str) -> List[str]:
        """
        Translates a single query into one or more variations.
        
        Args:
            query: The original user query.
            
        Returns:
            A list of translated queries (strings).
        """
        pass
