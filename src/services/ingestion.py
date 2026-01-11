import hashlib
import os
import glob
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument

from src.core.interfaces.vector_store import VectorStoreRepository
from src.core.interfaces.document_parser import DocumentParser
from src.utils.parsing import extract_email, extract_name, extract_address, extract_job_role

class IngestionService:
    """
    Business logic for document ingestion.
    Follows SRP and DIP.
    """
    def __init__(self, vector_store: VectorStoreRepository, parser: Optional[DocumentParser] = None):
        self.vector_store = vector_store
        self.parser = parser

    async def ingest_text(self, content: str, source_name: str, session_id: str):
        """
        Ingests raw text directly.
        """
        email = extract_email(content)
        if not email:
             raise ValueError(f"Could not find email in candidate data ({source_name}).")
        
        name = extract_name(content)
        role = extract_job_role(content)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # 1. State check (Optional: could be moved to repository or a separate StateService)
        # For Phase 3, we'll keep it simple or delegate to repository
        # await self.vector_store.delete_existing(email, session_id)

        # 2. Chunking
        documents = self._create_chunks(content, source_name, session_id, email, name, role, content_hash)
        
        # 3. Persistence
        await self.vector_store.add_documents(documents)
        print(f"Ingested {len(documents)} chunks (Vector) for {email}.")

    async def ingest_file(self, file_path: str, session_id: str, parser: Optional[DocumentParser] = None):
        """
        Parses and ingests a file.
        """
        effective_parser = parser or self.parser
        if not effective_parser:
             from src.infrastructure.parsers.factory import ParserFactory
             effective_parser = ParserFactory.get_parser(file_path)
             
        content = effective_parser.parse(file_path)
        await self.ingest_text(content, os.path.basename(file_path), session_id)

    def _create_chunks(self, content, source, session_id, email, name, role, content_hash=None):
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

# --- Backward Compatibility Layer (Phase 3) ---
from src.infrastructure.database.mongodb_vector import MongoDBVectorStore

async def ingest_single_cv(full_content: str, source_name: str, session_id: str):
    """Legacy entry point."""
    vector_store = MongoDBVectorStore()
    service = IngestionService(vector_store)
    await service.ingest_text(full_content, source_name, session_id)

async def ingest_directory(directory_path: str, session_id: str):
    """Legacy directory ingestion."""
    if not os.path.exists(directory_path):
        raise ValueError(f"Directory '{directory_path}' not found.")

    files = glob.glob(os.path.join(directory_path, "**/*.pdf"), recursive=True) + \
            glob.glob(os.path.join(directory_path, "**/*.txt"), recursive=True)

    summary = {"total": len(files), "successful": 0, "failed": 0, "errors": []}
    
    vector_store = MongoDBVectorStore()
    service = IngestionService(vector_store)

    for f in files:
        try:
            await service.ingest_file(f, session_id)
            summary["successful"] += 1
        except Exception as e:
            msg = f"Failed {os.path.basename(f)}: {str(e)}"
            summary["failed"] += 1
            summary["errors"].append(msg)
            print(msg)

    return summary
