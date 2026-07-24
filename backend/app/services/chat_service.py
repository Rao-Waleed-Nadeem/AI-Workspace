from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.providers.groq_provider import GroqProvider

from app.repositories.chat_repository import (
    create_chat,
)

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

        chat = create_chat(
            db=db,
            title="New Chat",
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

        return ChatResponse(
            message=reply,
        )
