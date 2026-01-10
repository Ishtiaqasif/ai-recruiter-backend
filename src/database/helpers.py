from .connection import get_db_client
from .config import DB_NAME, COLLECTION_NAME

def is_session_empty(session_id: str) -> bool:
    """Check if the given session has any documents in the database."""
    client = get_db_client()
    try:
        collection = client[DB_NAME][COLLECTION_NAME]
        count = collection.count_documents({"sessionId": session_id})
        return count == 0
    finally:
        client.close()
