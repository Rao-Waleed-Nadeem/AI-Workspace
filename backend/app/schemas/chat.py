from pydantic import BaseModel
from pydantic import  ConfigDict

from app.schemas.attachment import AttachmentResponse


class ChatRequest(BaseModel):

    chat_id: int | None = None
    action: str | None = None
    message: str
    document_id: int | None = None

class ChatResponse(BaseModel):
    chat_id: int
    message: str
    attachments: list[AttachmentResponse] = []

    model_config = ConfigDict(
        from_attributes=True,
    )