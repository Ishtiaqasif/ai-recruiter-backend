from abc import ABC, abstractmethod
from typing import List, Any
from langchain_core.messages import BaseMessage

class LLMInterface(ABC):
    """
    Abstract interface for LLM operations.
    Supports dependency inversion by allowing services to depend on this abstraction.
    """
    
    @abstractmethod
    async def invoke(self, messages: List[BaseMessage]) -> str:
        """
        Invokes the LLM with a list of messages.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Returns the name of the underlying model.
        """
        pass
