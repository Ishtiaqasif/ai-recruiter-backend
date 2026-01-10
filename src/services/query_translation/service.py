from typing import List, Set
from .base import BaseQueryTranslator

class QueryTranslationService:
    """Orchestrates query translation and multi-retrieval."""
    
    def __init__(self, translator: BaseQueryTranslator):
        self.translator = translator

    async def get_translated_queries(self, query: str) -> List[str]:
        """Returns a list of unique translated queries."""
        return await self.translator.translate(query)

    @staticmethod
    def deduplicate_docs(documents):
        """Helper to deduplicate documents based on page_content/metadata."""
        seen = set()
        unique_docs = []
        for doc in documents:
            # Using content as a simple proxy for uniqueness
            content = doc.page_content
            if content not in seen:
                seen.add(content)
                unique_docs.append(doc)
        return unique_docs
        
    async def retrieve_with_translation(self, query: str, vector_store, session_id: str):
        """
        Translates query and performs multiple searches, returning deduped docs.
        """
        queries = await self.get_translated_queries(query)
        all_docs = []
        
        for q in queries:
            results = vector_store.similarity_search(q, pre_filter={"sessionId": session_id})
            all_docs.extend(results)
            
        return self.deduplicate_docs(all_docs)
