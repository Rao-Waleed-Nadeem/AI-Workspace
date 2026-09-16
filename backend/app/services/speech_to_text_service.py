from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.providers.groq_speech_to_text_provider import (
    GroqSpeechToTextProvider,
)

ALLOWED_AUDIO_EXTENSIONS = {
    ".flac",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".ogg",
    ".wav",
    ".webm",
}

ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/flac",
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "video/mp4",
    "video/webm",
}


class SpeechToTextService:

    def __init__(self):
        self.provider = GroqSpeechToTextProvider()

    async def transcribe(
        self,
        file: UploadFile,
    ) -> str:

        self._validate_file(file)

        await file.seek(0)

        audio_size = await self._get_file_size(file)

        if audio_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded audio file is empty.",
            )

        if audio_size > settings.MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Audio file exceeds the maximum allowed size.",
            )

        await file.seek(0)

        try:
            transcript = self.provider.transcribe(
                file=file.file,
                filename=file.filename or "audio",
                content_type=file.content_type or "application/octet-stream",
            )

        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="Speech-to-text provider failed.",
            ) from exc

        finally:
            await file.close()

        if not transcript:
            raise HTTPException(
                status_code=422,
                detail="No speech could be transcribed from the audio.",
            )

        return transcript

    @staticmethod
    def _validate_file(file: UploadFile) -> None:
        filename = file.filename or ""
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail="Unsupported audio format.",
            )

        if file.content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
            raise HTTPException(
                status_code=415,
                detail="Unsupported audio MIME type.",
            )

    @staticmethod
    async def _get_file_size(file: UploadFile) -> int:
        await file.file.seek(0, 2)
        size = await file.file.tell()
        await file.file.seek(0)
        return size