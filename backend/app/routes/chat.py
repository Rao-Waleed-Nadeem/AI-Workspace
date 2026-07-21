from fastapi import APIRouter
from app.services.chat_service import ChatService

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

router = APIRouter()

chat_service = ChatService()

@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):
    return chat_service.generate_response(
        request
    )