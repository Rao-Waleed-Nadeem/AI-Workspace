from typing import BinaryIO

from groq import Groq

from app.core.config import settings
from app.providers.base_speech_to_text_provider import (
    BaseSpeechToTextProvider,
)


class GroqSpeechToTextProvider(BaseSpeechToTextProvider):

    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )

    def transcribe(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> str:

        transcription = self.client.audio.transcriptions.create(
            file=(filename, file.read()),
            model=settings.SPEECH_TO_TEXT_MODEL_NAME,
            response_format="json",
            temperature=0.0,
        )

        return transcription.text.strip()