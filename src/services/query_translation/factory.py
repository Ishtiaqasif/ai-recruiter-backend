from .base import BaseQueryTranslator, QueryTranslationType
from .identity import IdentityTranslator
from .multi_query import MultiQueryTranslator
from .hyde import HyDETranslator
from .decomposition import DecompositionTranslator
from .step_back import StepBackTranslator

class TranslatorFactory:
    """Factory for creating and managing query translators."""
    
    @staticmethod
    def get_translator(translator_type: str | QueryTranslationType, llm=None) -> BaseQueryTranslator:
        """
        Returns a concrete implementation of BaseQueryTranslator.
        
        Args:
            translator_type: The type of translator (str or QueryTranslationType enum)
            llm: Optional LLM instance required for some translators.
            
        Returns:
            A BaseQueryTranslator instance.
        """
        # Convert string to Enum if necessary
        if isinstance(translator_type, str):
            try:
                translator_type = QueryTranslationType(translator_type.lower())
            except ValueError:
                translator_type = QueryTranslationType.IDENTITY

        translators = {
            QueryTranslationType.MULTI_QUERY: MultiQueryTranslator,
            QueryTranslationType.HYDE: HyDETranslator,
            QueryTranslationType.DECOMPOSITION: DecompositionTranslator,
            QueryTranslationType.STEP_BACK: StepBackTranslator,
            QueryTranslationType.IDENTITY: IdentityTranslator
        }
        
        translator_class = translators.get(translator_type, IdentityTranslator)
        
        # If the translator requires an LLM but none is provided, fallback to identity
        if translator_class != IdentityTranslator and not llm:
            return IdentityTranslator()
            
        if translator_class == IdentityTranslator:
            return IdentityTranslator()
            
        return translator_class(llm=llm)
