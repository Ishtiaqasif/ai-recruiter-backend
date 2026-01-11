from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from src.config import APP_API_KEY
from src.infrastructure.llm.factory import LLMFactory
from src.infrastructure.database.mongodb_vector import MongoDBVectorStore
from src.services.chat import ChatService
from src.services.ingestion import IngestionService

# Security (API Key)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header_val: str = Security(api_key_header)):
    if not APP_API_KEY:
        return None
    if api_key_header_val == APP_API_KEY:
        return api_key_header_val
    raise HTTPException(status_code=403, detail="Could not validate credentials")

def get_chat_service() -> ChatService:
    llm = LLMFactory.get_llm()
    vector_store = MongoDBVectorStore()
    return ChatService(llm, vector_store)

def get_ingestion_service() -> IngestionService:
    vector_store = MongoDBVectorStore()
    return IngestionService(vector_store)
