from typing import List
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from src.core.interfaces.vector_store import VectorStoreRepository
from src.config import MONGODB_URI, DB_NAME, COLLECTION_NAME, MONGODB_VECTOR_INDEX
from src.database.embeddings import get_embeddings
from src.database.connection import get_db_client

class MongoDBVectorStore(VectorStoreRepository):
    def __init__(self):
        self.embeddings = get_embeddings()
        self.vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=MONGODB_URI,
            namespace=f"{DB_NAME}.{COLLECTION_NAME}",
            embedding=self.embeddings,
            index_name=MONGODB_VECTOR_INDEX,
        )

    async def add_documents(self, documents: List[Document]) -> None:
        await self.vector_store.aadd_documents(documents)

    async def similarity_search(self, query: str, session_id: str, k: int = 4) -> List[Document]:
        # Filter by sessionId
        return await self.vector_store.asimilarity_search(
            query=query,
            k=k,
            pre_filter={"sessionId": session_id}
        )

    async def delete_by_session(self, session_id: str) -> None:
        client = get_db_client()
        collection = client[DB_NAME][COLLECTION_NAME]
        collection.delete_many({"sessionId": session_id})
