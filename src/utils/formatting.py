import hashlib
from ..database import get_embedding_info, DB_NAME, COLLECTION_NAME

def generate_id(email: str, content: str, index: int, session_id: str) -> str:
    raw = f"{session_id}:{email}:{content}:{index}"
    hash_hex = hashlib.sha256(raw.encode()).hexdigest()
    return f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"

def print_ingestion_info():
    # Log configuration
    emb_info = get_embedding_info()
    print(f"--- Ingestion Info ---")
    print(f"Data Store Provider: mongodb")
    print(f"Database: {DB_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Embedding Provider: {emb_info['provider']}")
    print(f"Embedding Model: {emb_info['model']}")
    print(f"----------------------")
