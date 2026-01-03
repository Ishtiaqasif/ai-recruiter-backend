import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "rag_prototype")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME", "vector_index")

def get_db_client():
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set")
    return MongoClient(MONGODB_URI)

def get_embeddings():
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    
    if provider == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif provider == "ollama":
        return OllamaEmbeddings(model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"))
    elif provider == "google":
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    else:
        # Default fallback or error
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def get_vector_store():
    client = get_db_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    embeddings = get_embeddings()
    
    # Ensure index exists or is created (Atlas usually requires manual creation, but we can try)
    # For now returning the store object
    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
        relevance_score_fn="cosine",
    )
