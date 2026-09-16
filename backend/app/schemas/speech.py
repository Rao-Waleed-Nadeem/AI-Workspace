from pydantic import BaseModel


class SpeechToTextResponse(BaseModel):
    transcript: str