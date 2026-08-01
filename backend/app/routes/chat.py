from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.chat_service import ChatService

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()

chat_service = ChatService()


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):

    # print("request", request)
    return chat_service.generate_response(
        db,
        request,
    )


@router.post("/chat/stream")
def stream_response(
    request: ChatRequest,
    db: Session = Depends(get_db),
):

    return StreamingResponse(
        chat_service.stream_response(
            db=db,
            request=request,
        ),
        media_type="text/event-stream",
    )


@router.get("/chat/{chat_id}/messages")
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
):
    return chat_service.get_messages(
        db=db,
        chat_id=chat_id,
    )


@router.post("/chat/structured")
def structured_chat(
    request: ChatRequest,
):

    return chat_service.generate_structured_response(
        request,
    )
