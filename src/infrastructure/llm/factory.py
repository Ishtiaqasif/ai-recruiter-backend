from src.config import (
    LLM_PROVIDER, 
    OPENAI_LLM_MODEL, 
    GOOGLE_LLM_MODEL, 
    LOCAL_LLM_MODEL, 
    GOOGLE_API_KEY
)
from src.core.interfaces.llm import LLMInterface
from .openai import OpenAILLM
from .google import GoogleLLM
from .ollama import OllamaLLM

class LLMFactory:
    """
    Factory to create LLM instances based on configuration.
    Follows Open/Closed principle by centralizing creation.
    """
    
    @staticmethod
    def get_llm() -> LLMInterface:
        provider = LLM_PROVIDER.lower()
        
        if provider == "openai":
            return OpenAILLM(model_name=OPENAI_LLM_MODEL)
        elif provider in ["ollama", "local"]:
            return OllamaLLM(model_name=LOCAL_LLM_MODEL)
        elif provider == "google":
            return GoogleLLM(model_name=GOOGLE_LLM_MODEL, api_key=GOOGLE_API_KEY)
        
        # Default fallback
        return GoogleLLM(model_name=GOOGLE_LLM_MODEL, api_key=GOOGLE_API_KEY)
