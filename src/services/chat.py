from typing import List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

from src.core.interfaces.llm import LLMInterface
from src.core.interfaces.vector_store import VectorStoreRepository
from src.services.query_translation import TranslatorFactory, QueryTranslationService
from src.config import QUERY_TRANSLATION_TYPE

class ChatService:
    """
    Business logic for chat operations.
    Follows SRP and DIP by depending on interfaces.
    """
    def __init__(self, llm: LLMInterface, vector_store: VectorStoreRepository):
        self.llm = llm
        self.vector_store = vector_store

    def _format_docs(self, docs: List[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    async def ask(self, question: str, session_id: str) -> str:
        # 1. Retrieve related documents
        # We still use the translation service for now, but it's part of the retrieval strategy
        translator = TranslatorFactory.get_translator(QUERY_TRANSLATION_TYPE, llm=self.llm)
        translation_service = QueryTranslationService(translator)
        
        # Note: We need a bridge between our VectorStoreRepository and LangChain's VectorStore for the translation service
        # For simplicity in this phase, we'll manually handle retrieval or adapt the translation service
        # In a full refactor, translation_service would also depend on VectorStoreRepository
        
        # Temporary internal call to vector_store via translation
        # (Assuming translation_service.retrieve_with_translation still takes a langchain vector_store instance)
        # We might need to expose the raw vector store from the repository or refactor translation service.
        # For now, let's keep it direct to the repository if possible.
        
        docs = await self.vector_store.similarity_search(question, session_id)
        
        context = self._format_docs(docs)

        system_prompt = """You are an expert AI Recruiter Assistant.
        Use the following context (resumes/CVs) to answer the user's question.
        If the answer is not in the context, say you don't know.
        
        Context:
        {context}
        """
        
        messages = [
            SystemMessage(content=system_prompt.format(context=context)),
            HumanMessage(content=question)
        ]
        
        return await self.llm.invoke(messages)

# --- Backward Compatibility Layer (Phase 3) ---
from src.infrastructure.llm.factory import LLMFactory
from src.infrastructure.database.mongodb_vector import MongoDBVectorStore

async def ask_question(question: str, session_id: str):
    """
    Legacy entry point. Uses defaults.
    """
    llm = LLMFactory.get_llm()
    vector_store = MongoDBVectorStore()
    service = ChatService(llm, vector_store)
    return await service.ask(question, session_id)
