import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from src.database import get_vector_store, DB_NAME, COLLECTION_NAME
from src.utils.parsing import extract_email, extract_name, extract_address, extract_job_role
from src.utils.formatting import generate_id

async def ingest_single_cv(full_content: str, source_name: str, session_id: str):
    # Only Mongo
    await _ingest_mongo(full_content, source_name, session_id)

# _ingest_json removed

async def _ingest_mongo(full_content: str, source_name: str, session_id: str):
    """Full-featured ingestion for MongoDB with state tracking."""
    vector_store = get_vector_store()
    
    content_hash = hashlib.sha256(full_content.encode()).hexdigest()
    email = extract_email(full_content)
    
    if not email:
        raise ValueError(f"Could not find email in candidate data ({source_name}).")
        
    # Check existence
    # Check for existing documents for this candidate in this session
    from src.database import get_db_client
    client = get_db_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    
    # query for any document with this session and email
    # Mongo keys are flattened
    existing_doc = collection.find_one({"sessionId": session_id, "email": email})
    
    if existing_doc:
        old_hash = existing_doc.get("contentHash")
        if old_hash == content_hash:
            print(f"Skipping Mongo ingest: Content unchanged for {email} (Hash: {content_hash[:8]}...).")
            return
        else:
            print(f"Content changed for {email} in session {session_id} (old={str(old_hash)[:8]}..., new={content_hash[:8]}...). Updating MongoDB...")
            collection.delete_many({"sessionId": session_id, "email": email})

    name = extract_name(full_content)
    role = extract_job_role(full_content)
    
    documents = _create_chunks(full_content, source_name, session_id, email, name, role, content_hash)
    
    if not documents:
        return

    await vector_store.aadd_documents(documents)
    print(f"Ingested {len(documents)} chunks for {email} into MongoDB.")

def _create_chunks(content, source, session_id, email, name, role, content_hash=None):
    address = extract_address(content)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n----------------\n", "\nSECTION\n", "\n\n", "\n", " "]
    )
    
    split_docs = splitter.split_text(content)
    documents = []
    
    for i, chunk in enumerate(split_docs):
        enriched_content = f"CANDIDATE IDENTITY: {email}\nFULL NAME: {name}\nADDRESS: {address}\nJOB ROLE: {role}\n\n--- SECTION CONTENT ---\n{chunk}"
        
        metadata = {
            "sessionId": session_id,
            "email": email,
            "name": name,
            "role": role,
            "source": source
        }
        if content_hash:
            metadata["contentHash"] = content_hash
        
        documents.append(LCDocument(page_content=enriched_content, metadata=metadata))
    
    return documents