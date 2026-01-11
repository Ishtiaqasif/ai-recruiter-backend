from fastapi import APIRouter, Depends, Request
from src.api.v1.schemas import ChatRequest, ChatResponse
from src.api.v1.dependencies import get_api_key, get_chat_service
from src.services.chat import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse, summary="Chat with RAG", dependencies=[Depends(get_api_key)])
async def chat_endpoint(request: Request, chat_req: ChatRequest, service: ChatService = Depends(get_chat_service)):
    response = await service.ask(chat_req.question, chat_req.sessionId)
    return {"response": response}
