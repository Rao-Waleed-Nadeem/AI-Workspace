from pydantic import BaseModel, HttpUrl
import app.schemas.attachment as AttachmentResponse


class VisionChatResponse(BaseModel):
    chat_id: int | None = None
    message: str
    image_url: list[AttachmentResponse.AttachmentResponse] = []

from pydantic import BaseModel

