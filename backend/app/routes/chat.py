from fastapi import APIRouter
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


@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):

    return chat_service.generate_response(
        db,
        request,
    )
