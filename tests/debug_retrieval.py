import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.getcwd())

load_dotenv()

from src.database import get_vector_store, get_db_client, DB_NAME, COLLECTION_NAME
from src.services.ingestion import ingest_single_cv

SESSION_ID = "debug-retrieval-session"

async def debug_retrieval():
    print(f"--- Debugging Retrieval for Session: {SESSION_ID} ---")
    
    # 1. Ingest Data
    print("1. Ingesting data...")
    text = "CANDIDATE: Alice Debug\nEmail: debug@example.com\nSkill: Super Debugging Skills."
    await ingest_single_cv(text, "manual_test", SESSION_ID)
    
    # 2. Check Mongo directly
    print("2. Checking Mongo documents...")
    client = get_db_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    count = collection.count_documents({"sessionId": SESSION_ID})
    print(f"   Count in DB: {count}")
    
    if count > 0:
        doc = collection.find_one({"sessionId": SESSION_ID})
        print(f"   Sample Doc Keys: {doc.keys()}")
        print(f"   Sample Metadata Keys (should be flattened): {[k for k in doc.keys() if k not in ['embedding', 'page_content']]}")
    
    # 3. Perform Retrieval
    print("3. Performing Vector Search...")
    vector_store = get_vector_store()
    
    query = "What is Alice's skill?"
    
    # Simulate Chat Logic
    search_kwargs = {"k": 5}
    # Try standard 'filter' which maps to pre_filter in Atlas usually
    search_kwargs["pre_filter"] = {"sessionId": SESSION_ID}
    
    print(f"   Query: {query}")
    print(f"   Filters: {search_kwargs}")
    
    results = await vector_store.asimilarity_search(query, **search_kwargs)
    
    print(f"   Results Found: {len(results)}")
    for i, res in enumerate(results):
        print(f"   [{i}] Content: {res.page_content[:100]}...")
        print(f"        Metadata: {res.metadata}")

    # Cleanup
    collection.delete_many({"sessionId": SESSION_ID})
    print("--- Done ---")

if __name__ == "__main__":
    asyncio.run(debug_retrieval())
