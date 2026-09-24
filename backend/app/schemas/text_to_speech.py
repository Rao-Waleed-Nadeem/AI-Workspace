from pydantic import BaseModel, Field


class TextToSpeechRequest(BaseModel):
    text: str = Field(
        min_length=1,
    )


class TextToSpeechResponse(BaseModel):
    audio_chunks: list[str]