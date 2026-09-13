from datetime import datetime

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):

    prompt: str = Field(
        min_length=1,
        max_length=4000,
    )


class ImageGenerationResponse(BaseModel):

    id: int
    url: str
    expires_at: datetime