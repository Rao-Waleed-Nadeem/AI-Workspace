from pydantic import BaseModel


class ChatRequest(BaseModel):

    chat_id: int | None = None

    message: str


class ChatResponse(BaseModel):
    chat_id: int
    message: str
