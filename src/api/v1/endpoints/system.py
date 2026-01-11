from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.schemas import StandardResponse, WipeSessionRequest, StatusResponse
from src.api.v1.dependencies import get_api_key, get_ingestion_service, get_chat_service
from src.services.ingestion import IngestionService
from src.services.chat import ChatService

router = APIRouter(tags=["System"])

@router.post("/wipe", response_model=StandardResponse, summary="Clear Session Data", dependencies=[Depends(get_api_key)])
async def wipe_session(request: WipeSessionRequest, service: IngestionService = Depends(get_ingestion_service)):
    try:
        await service.vector_store.delete_by_session(request.sessionId)
        return {"status": "success", "message": f"Cleared session {request.sessionId}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}", response_model=StatusResponse, summary="Check Session Status", dependencies=[Depends(get_api_key)])
async def check_status(session_id: str):
    # This logic is currently in src/database/helpers.py, let's keep it simple for now
    from src.database.helpers import is_session_empty
    return {"isEmpty": is_session_empty(session_id)}

@router.get("/health", summary="Health Check")
async def health_check():
    return {"status": "healthy"}
