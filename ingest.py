import os
import re
import hashlib
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document as LCDocument
from database import get_vector_store, get_db_client, DB_NAME, COLLECTION_NAME

# Regex patterns
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
ROLE_KEYWORDS = ["Software Engineer", "Developer", "Manager", "Analyst", "Lead", "Architect", "Designer", "Consultant"]
ADDRESS_KEYWORDS = ["Street", "Avenue", "Road", "Rd", "St", "Ave", "Drive", "Dr", "Lane", "Ln", "City", "State", "Zip", "Country"]

def extract_email(text: str) -> Optional[str]:
    match = re.search(EMAIL_REGEX, text)
    return match.group(0).lower() if match else None

def extract_name(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line) < 50 and "@" not in first_line:
            return first_line
    return "Not Found"

def extract_address(text: str) -> str:
    lines = [l.strip() for l in text.split("\n")]
    for line in lines:
        if any(kw in line for kw in ADDRESS_KEYWORDS) and len(line) < 100:
            return line
    return "Not Found"

def extract_job_role(text: str) -> str:
    lines = [l.strip() for l in text.split("\n")]
    for line in lines:
        if any(kw.lower() in line.lower() for kw in ROLE_KEYWORDS) and len(line) < 60:
            return line
    return "Not Found"

def generate_id(email: str, content: str, index: int, session_id: str) -> str:
    raw = f"{session_id}:{email}:{content}:{index}"
    hash_hex = hashlib.sha256(raw.encode()).hexdigest()
    return f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"

async def ingest_single_cv(full_content: str, source_name: str, session_id: str):
    vector_store = get_vector_store()
    
    content_hash = hashlib.sha256(full_content.encode()).hexdigest()
    email = extract_email(full_content)
    
    if not email:
        raise ValueError(f"Could not find email in candidate data ({source_name}).")
        
    # Check existence
    client = get_db_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    
    # Check if already up to date
    existing = collection.find_one({
        "metadata.sessionId": session_id,
        "metadata.email": email,
        "metadata.contentHash": content_hash
    })
    
    if existing:
        print(f"Skipping: Data for {email} in session {session_id} is already up to date.")
        return

    # Check update
    is_update = collection.find_one({"metadata.sessionId": session_id, "metadata.email": email})
    if is_update:
        print(f"Changes detected for {email} in session {session_id}. Updating...")
        collection.delete_many({"metadata.sessionId": session_id, "metadata.email": email})

    name = extract_name(full_content)
    address = extract_address(full_content)
    role = extract_job_role(full_content)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n----------------\n", "\nSECTION\n", "\n\n", "\n", " "]
    )
    
    split_docs = splitter.split_text(full_content)
    
    documents = []
    for i, chunk in enumerate(split_docs):
        enriched_content = f"CANDIDATE IDENTITY: {email}\nFULL NAME: {name}\nADDRESS: {address}\nJOB ROLE: {role}\n\n--- SECTION CONTENT ---\n{chunk}"
        doc_id = generate_id(email, chunk, i, session_id)
        
        metadata = {
            "sessionId": session_id,
            "email": email,
            "name": name,
            "role": role,
            "contentHash": content_hash,
            "source": source_name
        }
        
        # We manually add id to metadata or handle it? 
        # Atlas Vector Search usually generates _id, but we can use our id as well if we pass ids argument
        # But LangChain add_documents doesn't easily take custom IDs unless we pass them separately
        documents.append(LCDocument(page_content=enriched_content, metadata=metadata))

    # Note: add_documents returns list of IDs. 
    # If we want to force our IDs we might need add_collection or similar, or just let Mongo generate _id
    await vector_store.aadd_documents(documents)
    print(f"Ingested {len(documents)} chunks for {email} in session {session_id}.")
