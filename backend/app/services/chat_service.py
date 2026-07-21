from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)


class ChatService:

    def generate_response(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

       reply = (
    f"You said: {request.message}"
)

       return ChatResponse(
    message=reply,
    )
