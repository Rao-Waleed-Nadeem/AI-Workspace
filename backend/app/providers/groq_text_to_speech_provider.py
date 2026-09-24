from pathlib import Path
from tempfile import NamedTemporaryFile

from groq import Groq

from app.core.config import settings
from app.providers.base_text_to_speech_provider import (
    BaseTextToSpeechProvider,
)


class GroqTextToSpeechProvider(
    BaseTextToSpeechProvider
):

    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )

    def synthesize(
        self,
        text: str,
        voice: str,
    ) -> bytes:

        response = self.client.audio.speech.create(
            model=settings.TEXT_TO_SPEECH_MODEL_NAME,
            voice=voice,
            input=text,
            response_format="wav",
        )

        with NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

        try:
            response.write_to_file(
                str(temporary_path)
            )

            return temporary_path.read_bytes()

        finally:
            temporary_path.unlink(
                missing_ok=True
            )