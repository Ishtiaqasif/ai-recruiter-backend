from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Routers
from src.api.v1.endpoints import chat, ingestion, system
from src.config import ALLOWED_ORIGINS
from src.services.prototype_seeding import seed_prototype_data_if_needed

load_dotenv()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

tags_metadata = [
    {"name": "General", "description": "Health check and system status endpoints."},
    {"name": "Ingestion", "description": "Endpoints for processing CVs and text."},
    {"name": "Chat", "description": "Interactive chat endpoints using RAG."},
    {"name": "System", "description": "System and Session management."},
]

app = FastAPI(
    title="AI Recruiter RAG API (SOLID)",
    description="Backend API refactored to follow SOLID principles.",
    version="2.0.0",
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

# Include Routers
app.include_router(system.router)
app.include_router(ingestion.router)
app.include_router(chat.router)

@app.on_event("startup")
async def startup_event():
    # Automated Seeding for Prototypes
    await seed_prototype_data_if_needed()

@app.get("/", tags=["General"], summary="Root Endpoint")
def read_root():
    return {"status": "ok", "message": "SOLID Backend is running"}

# Standardized Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail},
        )
    
    print(f"CRITICAL ERROR: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal Server Error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
