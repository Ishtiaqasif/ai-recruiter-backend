import asyncio
from typing import List
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.documents import Document
from src.core.interfaces.llm import LLMInterface
from src.core.interfaces.vector_store import VectorStoreRepository
from src.services.chat import ChatService

class MockLLM(LLMInterface):
    async def invoke(self, messages: List[BaseMessage]) -> str:
        return "Mock Response"
    def get_model_name(self) -> str:
        return "mock-model"

class MockVectorStore(VectorStoreRepository):
    async def add_documents(self, documents: List[Document]) -> None:
        pass
    async def similarity_search(self, query: str, session_id: str, k: int = 4) -> List[Document]:
        return [Document(page_content="Mock Context")]
    async def delete_by_session(self, session_id: str) -> None:
        pass

async def test_chat_service_solid():
    print("Testing ChatService with SOLID (DI)...")
    mock_llm = MockLLM()
    mock_vs = MockVectorStore()
    
    service = ChatService(llm=mock_llm, vector_store=mock_vs)
    response = await service.ask("Hello?", "session_123")
    
    assert response == "Mock Response"
    print("✅ ChatService test passed!")

if __name__ == "__main__":
    asyncio.run(test_chat_service_solid())
