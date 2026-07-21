from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.providers.groq_provider import (
    GroqProvider,
)

provider = GroqProvider()


class ChatService:

    def generate_response(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        reply = provider.generate_response(request.message)

        return ChatResponse(message=reply)
