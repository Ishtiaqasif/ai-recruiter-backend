import os
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from .config import (
    EMBEDDING_LLM_PROVIDER,
    OPENAI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
    GOOGLE_EMBEDDING_MODEL
)

def get_embeddings():
    provider = EMBEDDING_LLM_PROVIDER
    
    if provider == "openai":
        return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    elif provider == "local":
        return OllamaEmbeddings(model=LOCAL_EMBEDDING_MODEL)
    elif provider == "google":
        return GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)
    else:
        # Default fallback
        return GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

def get_embedding_info() -> dict:
    provider = EMBEDDING_LLM_PROVIDER
    model_name = "Unknown"
    
    if provider == "openai":
        model_name = OPENAI_EMBEDDING_MODEL
    elif provider == "local":
        model_name = LOCAL_EMBEDDING_MODEL
    elif provider == "google":
        model_name = GOOGLE_EMBEDDING_MODEL
    else:
        model_name = GOOGLE_EMBEDDING_MODEL
        
    return {
        "provider": provider,
        "model": model_name
    }
