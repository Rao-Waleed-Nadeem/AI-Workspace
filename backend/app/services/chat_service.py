from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.providers.groq_provider import GroqProvider

from app.repositories.chat_repository import create_chat, get_chat

from app.repositories.message_repository import create_message, get_chat_messages

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

            history = get_chat_messages(
                db=db,
                chat_id=chat.id,
            )

            conversation = []

            for message in history:
                conversation.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

            reply = provider.generate_response(
                conversation,
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

    def stream_response(
        self,
        db: Session,
        request: ChatRequest,
    ):

        try:
            if request.chat_id is None:

                chat = create_chat(
                    db=db,
                    title="New Chat",
                )

            else:

                chat = get_chat(
                    db=db,
                    chat_id=request.chat_id,
                )

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

            history = get_chat_messages(
                db=db,
                chat_id=chat.id,
            )

            conversation = []

            for message in history:
                conversation.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

            full_response = ""

            # Send chat_id as the first SSE event so the client can track the conversation
            yield f"event: chat_id\ndata: {chat.id}\n\n"

            for token in provider.stream_response(conversation):

                full_response += token

                yield f"data: {token}\n\n"

            create_message(
                db=db,
                chat_id=chat.id,
                role="assistant",
                content=full_response,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise
