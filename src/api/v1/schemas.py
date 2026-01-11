from pydantic import BaseModel
from typing import List, Optional

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
