import os
from langchain_mongodb import MongoDBAtlasVectorSearch
from .config import (
    MONGODB_URI,
    DB_NAME, 
    COLLECTION_NAME, 
    MONGODB_VECTOR_INDEX
)
from .connection import get_db_client
from .embeddings import get_embeddings

def get_vector_store():
    embeddings = get_embeddings()
    # Always Mongo
    return MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=MONGODB_URI,
        namespace=DB_NAME+"."+COLLECTION_NAME,
        embedding=embeddings,
        index_name=MONGODB_VECTOR_INDEX,
    )

# Wrapper removed
