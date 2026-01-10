from typing import List
from .base import BaseQueryTranslator

class IdentityTranslator(BaseQueryTranslator):
    """Fallback translator that returns the original query as-is."""
    
    async def translate(self, query: str) -> List[str]:
        return [query]
