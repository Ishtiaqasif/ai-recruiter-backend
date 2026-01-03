from pymongo import MongoClient
from .config import MONGODB_URI

def get_db_client():
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not set")
    return MongoClient(MONGODB_URI)
