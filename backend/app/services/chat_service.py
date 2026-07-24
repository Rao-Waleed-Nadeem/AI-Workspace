from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.providers.groq_provider import GroqProvider

from app.repositories.chat_repository import create_chat, get_chat

from app.repositories.message_repository import (
    create_message,
)

provider = GroqProvider()


class ChatService:

    def generate_response(
        self,
        db: Session,
        request: ChatRequest,
    ) -> ChatResponse:

        try:
            if request.chat_id is None:

                chat = create_chat(
                    db=db,
                    title="New Chat",
                )
                print("chat", chat)

            else:

                chat = get_chat(
                    db=db,
                    chat_id=request.chat_id,
                )
                print("chat", chat)

                if chat is None:

                    raise HTTPException(
                        status_code=404,
                        detail="Chat not found",
                    )

            create_message(
                db=db,
                chat_id=chat.id,
                role="user",
                content=request.message,
            )

            reply = provider.generate_response(
                request.message,
            )

            create_message(
                db=db,
                chat_id=chat.id,
                role="assistant",
                content=reply,
            )

            db.commit()

            print("reply", reply)

            return ChatResponse(
                chat_id=chat.id,
                message=reply,
            )

        except Exception:
            db.rollback()
            raise
