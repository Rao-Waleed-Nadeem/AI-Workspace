from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.chat_service import ChatService

from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from app.core.dependencies import get_current_user
from app.models import User

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
    current_user: User = Depends(get_current_user),
):

    # print("request", request)
    return chat_service.generate_response(
        db,
        request,
        user_id=current_user.id,
    )


@router.post("/chat/stream")
def stream_response(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return StreamingResponse(
        chat_service.stream_response(
            db=db,
            request=request,
            user_id=current_user.id,
        ),
        media_type="text/event-stream",
    )


@router.get("/chat/{chat_id}/messages")
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_messages(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )


@router.post("/chat/structured")
def structured_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return chat_service.generate_structured_response(
        db=db,
        request=request,
        user_id=current_user.id,
    )


@router.post("/chat/tools")
def tool_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return chat_service.generate_tool_response(
        db=db,
        request=request,
        user_id=current_user.id,
    )


@router.post("/chat/vision")
async def vision_chat(
    message: str = Form(...),
    chat_id: int | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = ChatRequest(
        chat_id=chat_id,
        message=message,
    )
    return await chat_service.generate_vision_response(
        db=db,
        request=request,
        image=image,
        user_id=current_user.id,
    )
