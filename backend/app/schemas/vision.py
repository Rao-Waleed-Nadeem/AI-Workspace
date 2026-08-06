from pydantic import BaseModel, HttpUrl


class VisionChatRequest(BaseModel):
    chat_id: int | None = None
    message: str
    image_url: HttpUrl

from pydantic import BaseModel

