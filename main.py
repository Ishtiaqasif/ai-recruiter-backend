from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import shutil
import tempfile
from ingest import ingest_single_cv
from chat import ask_question
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader


tags_metadata = [
    {
        "name": "General",
        "description": "Health check and system status endpoints.",
    },
    {
        "name": "Ingestion",
        "description": "Endpoints for uploading and processing CVs and text.",
    },
    {
        "name": "Chat",
        "description": "Interactive chat endpoints using RAG.",
    },
    {
        "name": "Session Management",
        "description": "Manage user sessions and data.",
    },
]

app = FastAPI(
    title="AI Recruiter RAG API",
    description="Backend API for the AI Recruiter system. Handles document ingestion, vector storage, and RAG-based chat operations.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    sessionId: str

class IngestTextRequest(BaseModel):
    text: str
    sessionId: str

class WipeSessionRequest(BaseModel):
    sessionId: str

class StandardResponse(BaseModel):
    status: str
    message: str

class ChatResponse(BaseModel):
    response: str

class StatusResponse(BaseModel):
    isEmpty: bool

@app.get("/", tags=["General"], summary="Root Endpoint")
def read_root():
    return {"status": "ok", "message": "Backend is running"}

@app.get("/health", tags=["General"], summary="Health Check")
def health_check():
    return {"status": "healthy"}

@app.post("/ingest", tags=["Ingestion"], summary="Ingest Document", response_model=StandardResponse)
async def ingest_document(
    file: UploadFile = File(..., description="The CV file (PDF or Text) to ingest"),
    sessionId: str = Form(..., description="Unique session identifier")
):
    try:
        # Create temp file
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        content = ""
        try:
            if suffix.lower() == ".pdf":
                loader = PyPDFLoader(tmp_path)
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
            else:
                loader = TextLoader(tmp_path)
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
        finally:
            os.unlink(tmp_path)

        await ingest_single_cv(content, file.filename, sessionId)
        return {"status": "success", "message": f"Ingested {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/text", tags=["Ingestion"], summary="Ingest Raw Text", response_model=StandardResponse)
async def ingest_text(
    request: IngestTextRequest,
):
    try:
        await ingest_single_cv(request.text, "raw_text_input", request.sessionId)
        return {"status": "success", "message": "Ingested text"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wipe", tags=["Session Management"], summary="Wipe Session Data", response_model=StandardResponse)
async def wipe_session(request: WipeSessionRequest):
    try:
        sessionId = request.sessionId
        # Logic to wipe (delete from mongo)
        from database import get_db_client, DB_NAME, COLLECTION_NAME
        client = get_db_client()
        collection = client[DB_NAME][COLLECTION_NAME]
        collection.delete_many({"metadata.sessionId": sessionId})
        return {"status": "success", "message": "Session wiped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", tags=["Session Management"], summary="Get Session Status", response_model=StatusResponse)
async def get_status(sessionId: str):
    # Check if any docs exist for session
    from database import get_db_client, DB_NAME, COLLECTION_NAME
    client = get_db_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    count = collection.count_documents({"metadata.sessionId": sessionId})
    return {"isEmpty": count == 0}

@app.post("/chat", tags=["Chat"], summary="Chat with RAG", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await ask_question(request.question, request.sessionId)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
