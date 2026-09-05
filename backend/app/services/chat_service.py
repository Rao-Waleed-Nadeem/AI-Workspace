import json

from groq import APIStatusError

from app.tools.definitions import CALCULATOR_TOOL
from app.tools.registry import TOOLS

from app.core.config import settings

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.prompts.rag import build_rag_prompt
from app.services.rag_context_service import (
    RetrievedChunk,
    build_rag_context,
)
from app.services.retrieval_service import RetrievalService

from app.services.rag_validation_service import (
    validate_document_for_rag,
    validate_retrieval_results,
)

from app.services.rag_failure_service import (
    get_rag_failure_message,
)


from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.schemas.attachment import AttachmentResponse

from fastapi import UploadFile

from app.utils.image_validator import (
    validate_image,
    validate_size,
)

from app.utils.image_encoder import (
    encode_image,
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
from app.repositories.attachment_repository import create_attachment
from app.utils.file_storage import save_uploaded_file
from app.services.rag_citation_service import (
    build_rag_sources,
    format_rag_sources,
    serialize_rag_sources,
)
from app.services.rag_exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    InsufficientContextError,
    NoRelevantContextError,
    UnsupportedDocumentError,
)

provider = GroqProvider()


def build_limited_conversation(
    history,
    *,
    transform_message=None,
) -> list[dict]:

    recent_history = history[-settings.CHAT_HISTORY_MESSAGE_LIMIT :]

    conversation = []
    total_characters = 0

    for message in reversed(recent_history):

        content = message.content

        if transform_message is not None:
            content = transform_message(message, content)

        remaining_characters = (
            settings.CHAT_HISTORY_MAX_CHARACTERS
            - total_characters
        )

        if remaining_characters <= 0:
            break

        if len(content) > remaining_characters:
            content = content[-remaining_characters:]

        conversation.append(
            {
                "role": message.role,
                "content": content,
            }
        )

        total_characters += len(content)

    return list(reversed(conversation))


def get_model_limit_message() -> str:

    return (
        "This chat has grown too large for the current model limit. "
        "I kept your saved chat history visible, but only the most recent "
        "messages can be sent to the model. Please try again with a shorter "
        "message or start a new chat."
    )


class ChatService:

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()

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

            conversation = build_limited_conversation(
                history,
            )

            rag_sources = []

            if request.document_id is not None:

                validate_document_for_rag(
                    db=db,
                    document_id=request.document_id,
                    user_id=user_id,
                )

                retrieval_results = self.retrieval_service.retrieve(
                    db=db,
                    question=request.message,
                    user_id=user_id,
                    document_id=request.document_id,
                    top_k=settings.RAG_TOP_K,
                    min_similarity=settings.RAG_MIN_SIMILARITY,
                )

                validate_retrieval_results(
                    retrieval_results,
                )

                chunks = [
                    RetrievedChunk(
                        document_id=result.document_id,
                        page_number=result.page_number,
                        content=result.content,
                    )
                    for result in retrieval_results
                ]

                context = build_rag_context(
                    chunks,
                )

                if not context.strip():
                    raise EmptyDocumentError("Retrieved context is empty.")

                rag_prompt = build_rag_prompt(
                    context=context,
                    question=request.message,
                )

                conversation = [
                    {
                        "role": "user",
                        "content": rag_prompt,
                    }
                ]

                rag_sources = build_rag_sources(
                    db=db,
                    results=retrieval_results,
                    user_id=user_id,
                )

            reply = provider.generate_response(
                conversation,
            )

            if rag_sources:
                formatted_sources = format_rag_sources(
                    rag_sources,
                )

                reply = f"{reply.rstrip()}" f"\n\n" f"{formatted_sources}"

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

            # -------------------------------------------------
            # Get or create chat
            # -------------------------------------------------

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

            yield ("event: chat_id\n" f"data: {chat.id}\n\n")

            # -------------------------------------------------
            # Save user message
            # -------------------------------------------------

            user_message = create_message(
                db=db,
                chat_id=chat.id,
                role="user",
                content=request.message,
            )

            # -------------------------------------------------
            # Load conversation history
            # -------------------------------------------------

            history = get_chat_messages(
                db=db,
                chat_id=chat.id,
                user_id=user_id,
            )

            def transform_stream_message(message, content):

                if message.id == user_message.id and request.action == "explain":
                    return build_explain_prompt(
                        content,
                    )

                return content

            conversation = build_limited_conversation(
                history,
                transform_message=transform_stream_message,
            )

            # -------------------------------------------------
            # RAG setup
            # -------------------------------------------------

            rag_sources = []

            if request.document_id is not None:

                try:

                    # -----------------------------------------
                    # Validate document
                    # -----------------------------------------

                    validate_document_for_rag(
                        db=db,
                        document_id=request.document_id,
                        user_id=user_id,
                    )

                    # -----------------------------------------
                    # Retrieve relevant chunks
                    # -----------------------------------------

                    retrieval_results = self.retrieval_service.retrieve(
                        db=db,
                        question=request.message,
                        user_id=user_id,
                        document_id=request.document_id,
                        top_k=settings.RAG_TOP_K,
                        min_similarity=settings.RAG_MIN_SIMILARITY,
                    )

                    # -----------------------------------------
                    # Validate retrieval results
                    # -----------------------------------------

                    validate_retrieval_results(
                        retrieval_results,
                    )

                    # -----------------------------------------
                    # Build RAG chunks
                    # -----------------------------------------

                    chunks = [
                        RetrievedChunk(
                            document_id=result.document_id,
                            page_number=result.page_number,
                            content=result.content,
                        )
                        for result in retrieval_results
                    ]

                    # -----------------------------------------
                    # Build context
                    # -----------------------------------------

                    context = build_rag_context(
                        chunks,
                    )

                    if not context.strip():

                        raise EmptyDocumentError("Retrieved context is empty.")

                    # -----------------------------------------
                    # Build RAG prompt
                    # -----------------------------------------

                    rag_prompt = build_rag_prompt(
                        context=context,
                        question=request.message,
                    )

                    # -----------------------------------------
                    # Replace normal conversation with
                    # document-grounded RAG prompt
                    # -----------------------------------------

                    conversation = [
                        {
                            "role": "user",
                            "content": rag_prompt,
                        }
                    ]

                    # -----------------------------------------
                    # Build citations
                    # -----------------------------------------

                    rag_sources = build_rag_sources(
                        db=db,
                        results=retrieval_results,
                        user_id=user_id,
                    )

                except (
                    DocumentNotFoundError,
                    UnsupportedDocumentError,
                    EmptyDocumentError,
                    NoRelevantContextError,
                    InsufficientContextError,
                ) as error:

                    failure_message = get_rag_failure_message(
                        error,
                    )

                    # Send controlled RAG error to frontend.
                    yield (
                        "event: rag_error\n" f"data: {json.dumps(failure_message)}\n\n"
                    )

                    # Persist the failure response.
                    create_message(
                        db=db,
                        chat_id=chat.id,
                        role="assistant",
                        content=failure_message,
                    )

                    db.commit()

                    return

            # -------------------------------------------------
            # Full streamed response
            # -------------------------------------------------

            full_response = ""

            # -------------------------------------------------
            # SSE: chat ID
            # -------------------------------------------------

            # yield ("event: chat_id\n" f"data: {chat.id}\n\n")

            # -------------------------------------------------
            # Stream AI response
            # -------------------------------------------------

            try:
                response_stream = provider.stream_response(
                    conversation,
                )

                for token in response_stream:

                    full_response += token

                    # Normalize line endings for SSE.
                    token = token.replace(
                        "\r\n",
                        "\n",
                    ).replace(
                        "\r",
                        "\n",
                    )

                    # SSE requires every line to have
                    # its own data: prefix.
                    for line in token.split("\n"):
                        yield f"data: {line}\n"

                    # Blank line terminates this SSE event.
                    yield "\n"

            except APIStatusError as error:

                if error.status_code == 413:

                    failure_message = get_model_limit_message()

                    yield (
                        "event: stream_error\n"
                        f"data: {json.dumps(failure_message)}\n\n"
                    )

                    create_message(
                        db=db,
                        chat_id=chat.id,
                        role="assistant",
                        content=failure_message,
                    )

                    db.commit()

                    return

                raise

            # -------------------------------------------------
            # Add citations
            # -------------------------------------------------

            final_response = full_response

            if rag_sources:

                formatted_sources = format_rag_sources(
                    rag_sources,
                )

                # Send citations to frontend.
                yield (
                    "event: sources\n"
                    f"data: {json.dumps(serialize_rag_sources(rag_sources))}\n\n"
                )

                # Persist citations together with answer.
                final_response = (
                    f"{full_response.rstrip()}" f"\n\n" f"{formatted_sources}"
                )

            # -------------------------------------------------
            # Save assistant response
            # -------------------------------------------------

            create_message(
                db=db,
                chat_id=chat.id,
                role="assistant",
                content=final_response,
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

            def transform_structured_message(message, content):

                if message.id == user_message.id:
                    return build_structured_analysis_prompt(
                        content,
                    )

                return content

            conversation = build_limited_conversation(
                history,
                transform_message=transform_structured_message,
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

            conversation = build_limited_conversation(
                history,
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

    async def generate_vision_response(
        self,
        db: Session,
        request: ChatRequest,
        image: UploadFile,
        user_id: int,
    ):
        await validate_size(image)

        validate_image(image)

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

            saved_file = await save_uploaded_file(
                image,
            )

            user_message = create_message(
                db=db,
                chat_id=chat.id,
                role="user",
                content=request.message,
            )

            attachment = create_attachment(
                db=db,
                message_id=user_message.id,
                attachment_type=saved_file["attachment_type"],
                mime_type=saved_file["mime_type"],
                original_name=saved_file["original_name"],
                storage_path=saved_file["storage_path"],
                size=saved_file["size"],
            )

            image_data = await encode_image(
                image,
            )

            history = get_chat_messages(
                db=db,
                chat_id=chat.id,
                user_id=user_id,
            )

            history = history[-4:]

            conversation = []

            for history_message in history:

                content = [
                    {
                        "type": "text",
                        "text": history_message.content,
                    }
                ]

                # Only attach the uploaded image to the CURRENT user message
                if history_message.id == user_message.id:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data,
                            },
                        }
                    )

                conversation.append(
                    {
                        "role": history_message.role,
                        "content": content,
                    }
                )

            reply = provider.generate_vision_response(
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
                attachments=[AttachmentResponse.model_validate(attachment)],
            )

        except Exception:
            db.rollback()
            raise
