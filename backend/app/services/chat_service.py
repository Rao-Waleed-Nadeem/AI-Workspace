from httpcore import request
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.providers.groq_provider import GroqProvider

from app.prompts.prompt_service import build_explain_prompt

from app.schemas.structured_output import StructuredResponse

from app.prompts.prompt_service import (
    build_structured_analysis_prompt,
)

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

            user_message = create_message(
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
                content = message.content
                if message.id == user_message.id and request.action == "explain":
                    content = build_explain_prompt(
                        message.content,
                    )

                conversation.append(
                    {
                        "role": message.role,
                        "content": content,
                    }
                )

            full_response = ""

            # Send chat_id as the first SSE event so the client can track the conversation
            yield f"event: chat_id\ndata: {chat.id}\n\n"

            for token in provider.stream_response(conversation):

                full_response += token
                # Normalize line endings for SSE
                token = token.replace("\r\n", "\n").replace("\r", "\n")

                # SSE requires each line of data to have its own "data:" prefix
                for line in token.split("\n"):
                    yield f"data: {line}\n"

                yield "\n"

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

    def get_messages(
        self,
        db: Session,
        chat_id: int,
    ):
        chat = get_chat(
            db=db,
            chat_id=chat_id,
        )

        if chat is None:
            raise HTTPException(
                status_code=404,
                detail="Chat not found",
            )

        return get_chat_messages(
            db=db,
            chat_id=chat_id,
        )

    def generate_structured_response(
        self,
        db: Session,
        request: ChatRequest,
    ) -> StructuredResponse:

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

            user_message = create_message(
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

                content = message.content

                if message.id == user_message.id:

                    content = build_structured_analysis_prompt(
                        message.content,
                    )

                conversation.append(
                    {
                        "role": message.role,
                        "content": content,
                    }
                )

            response = provider.generate_structured_response(
                conversation,
            )

            structured_response = StructuredResponse.model_validate_json(
                response,
            )

            create_message(
                db=db,
                chat_id=chat.id,
                role="assistant",
                content=structured_response.model_dump_json(),
            )

            db.commit()

            return structured_response

        except Exception:

            db.rollback()
            raise
