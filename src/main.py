from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os
import shutil
import tempfile
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import services
from src.services.ingestion import ingest_single_cv, ingest_directory
from src.services.chat import ask_question
from src.database import get_db_client, DB_NAME, COLLECTION_NAME
from src.config import ALLOWED_ORIGINS, APP_API_KEY
from src.core.constants import PrototypeConstants
from src.services.prototype_seeding import seed_prototype_data_if_needed

load_dotenv()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Security (API Key)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not APP_API_KEY:
        # If no key configured on server, allow all (Open Mode) or Fail Safe?
        # For production readiness, we should Log a warning but maybe allow if user forgot to set it?
        # BETTER: Fail safe. If intended for prod, security must be on.
        # However, for ease of transition, let's treat unset as "no auth".
        return None
    
    if api_key_header == APP_API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

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

# Secure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.on_event("startup")
async def startup_event():
    # Automated Seeding for Prototypes
    await seed_prototype_data_if_needed()

# Standardized Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Pass through HTTPExceptions
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail},
        )
            
    # In production, likely do not want to return exact string
    # For now, return the string but ensure 500
    print(f"Global Error: {exc}") # Log for internal debug
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal Server Error"}
    )

class ChatRequest(BaseModel):
    question: str
    sessionId: str

class IngestTextRequest(BaseModel):
    text: str
    sessionId: str

class WipeSessionRequest(BaseModel):
    sessionId: str

class IngestionSummaryResponse(BaseModel):
    total: int
    successful: int
    failed: int
    errors: list[str]

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

@app.post("/ingest", tags=["Ingestion"], summary="Ingest Document", response_model=StandardResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
async def ingest_document(
    request: Request,
    file: UploadFile = File(..., description="The CV file (PDF or Text) to ingest"),
    sessionId: str = Form(..., description="Unique session identifier")
):
    try:
        # File Size Validation (Max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > MAX_FILE_SIZE:
             raise HTTPException(status_code=413, detail="File too large (Max 10MB)")

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/text", tags=["Ingestion"], summary="Ingest Raw Text", response_model=StandardResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
async def ingest_text(
    request: Request,
    ingest_req: IngestTextRequest,
):
    try:
        await ingest_single_cv(ingest_req.text, "raw_text_input", ingest_req.sessionId)
        return {"status": "success", "message": "Ingested text"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/sample", tags=["Ingestion"], summary="Ingest Sample Data (data/top10)", response_model=IngestionSummaryResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("5/minute")
async def ingest_sample_data(
    request: Request,
    ingest_req: WipeSessionRequest # Reuse sessionId request model
):
    try:
        sample_dir = os.path.join(os.getcwd(), "data", "top10")
        summary = await ingest_directory(sample_dir, ingest_req.sessionId)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wipe", tags=["Session Management"], summary="Wipe Session Data", response_model=StandardResponse, dependencies=[Depends(get_api_key)])
async def wipe_session(request: WipeSessionRequest):
    try:
        sessionId = request.sessionId
        client = get_db_client() 
        collection = client[DB_NAME][COLLECTION_NAME]
        
        # Real Mongo
        collection.delete_many({"sessionId": sessionId})
             
        return {"status": "success", "message": "Session wiped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", tags=["Session Management"], summary="Get Session Status", response_model=StatusResponse, dependencies=[Depends(get_api_key)])
async def get_status(sessionId: str):
    # Check if any docs exist for session
    client = get_db_client() 
    collection = client[DB_NAME][COLLECTION_NAME]
    
    count = collection.count_documents({"sessionId": sessionId})
            
    return {"isEmpty": count == 0}

@app.post("/chat", tags=["Chat"], summary="Chat with RAG", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("20/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    try:
        response = await ask_question(chat_req.question, chat_req.sessionId)
        return {"response": response}
    except Exception as e:
        # This is caught by global handler for 500s usually, but valid to raise explicit HTTPExceptions
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use src.main:app since we are inside src but running from root usually
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
