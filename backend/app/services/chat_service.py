import json

from app.tools.definitions import CALCULATOR_TOOL
from app.tools.registry import TOOLS

from httpcore import request
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.providers.groq_provider import GroqProvider

from app.prompts.prompt_service import build_explain_prompt

from app.schemas.structured_output import (
    StructuredResponse,
    StructuredAIResponse,
)

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
        user_id: int,
    ) -> ChatResponse:

        try:
            if request.chat_id is None:

                chat = create_chat(
                    db=db,
                    title="New Chat",
                    user_id=user_id,
                )
                print("chat", chat)

            else:

                chat = get_chat(
                    db=db,
                    chat_id=request.chat_id,
                    user_id=user_id,
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
                user_id=user_id,
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
        user_id: int,
    ):

        try:
            if request.chat_id is None:

                chat = create_chat(
                    db=db,
                    title="New Chat",
                    user_id=user_id,
                )

            else:

                chat = get_chat(
                    db=db,
                    chat_id=request.chat_id,
                    user_id=user_id,
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
                user_id=user_id,
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
        user_id: int,
    ):
        chat = get_chat(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
        )

        if chat is None:
            raise HTTPException(
                status_code=404,
                detail="Chat not found",
            )

        return get_chat_messages(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
        )

    def generate_structured_response(
        self,
        db: Session,
        request: ChatRequest,
        user_id: int,
    ) -> StructuredResponse:

        try:

            if request.chat_id is None:

                chat = create_chat(
                    db=db,
                    title="New Chat",
                    user_id=user_id,
                )

            else:

                chat = get_chat(
                    db=db,
                    chat_id=request.chat_id,
                    user_id=user_id,
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
                user_id=user_id,
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

            ai_response = StructuredAIResponse.model_validate_json(
                response,
            )

            structured_response = StructuredResponse(
                chat_id=chat.id,
                title=ai_response.title,
                summary=ai_response.summary,
                keywords=ai_response.keywords,
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

    def generate_tool_response(
        self,
        db: Session,
        request: ChatRequest,
        user_id: int,
    ) -> ChatResponse:

        try:

            if request.chat_id is None:

                chat = create_chat(
                    db=db,
                    title="New Chat",
                    user_id=user_id,
                )

            else:

                chat = get_chat(
                    db=db,
                    chat_id=request.chat_id,
                    user_id=user_id,
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
                user_id=user_id,
            )

            conversation = []

            for message in history:
                conversation.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

            response_message = provider.generate_with_tools(
                conversation,
                [CALCULATOR_TOOL],
            )

            if response_message.tool_calls:

                tool_call = response_message.tool_calls[0]

                tool_name = tool_call.function.name

                arguments = json.loads(tool_call.function.arguments)

                tool = TOOLS.get(tool_name)

                if tool is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Unknown tool",
                    )

                tool_result = tool(**arguments)

                conversation.append(response_message)
               
                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result,
                    }
                )

                final_message = provider.generate_with_tools(
                    conversation,
                    [CALCULATOR_TOOL],
                )

                reply = final_message.content

            else:

                reply = response_message.content

            create_message(
                db=db,
                chat_id=chat.id,
                role="assistant",
                content=reply,
            )

            db.commit()

            return ChatResponse(
                chat_id=chat.id,
                message=reply,
            )

        except Exception:

            db.rollback()
            raise
