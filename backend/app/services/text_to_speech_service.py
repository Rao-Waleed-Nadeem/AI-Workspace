import re

from fastapi import HTTPException

from app.core.config import settings
from app.providers.groq_text_to_speech_provider import (
    GroqTextToSpeechProvider,
)


class TextToSpeechService:

    def __init__(self):
        self.provider = (
            GroqTextToSpeechProvider()
        )

    def synthesize(
        self,
        text: str,
    ) -> list[bytes]:

        if not settings.TEXT_TO_SPEECH_MODEL_NAME or not settings.TEXT_TO_SPEECH_VOICE:
            return []

        cleaned_text = self._clean_text(
            text
        )

        if not cleaned_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Text for speech "
                    "cannot be empty."
                ),
            )

        if (
            len(cleaned_text)
            > settings.MAX_TEXT_TO_SPEECH_CHARACTERS
        ):
            raise HTTPException(
                status_code=413,
                detail=(
                    "Text is too long "
                    "for speech generation."
                ),
            )

        chunks = self._split_text(
            cleaned_text,
            settings.TEXT_TO_SPEECH_CHUNK_SIZE,
        )

        audio_chunks: list[bytes] = []

        try:

            for chunk in chunks:

                audio_chunks.append(
                    self.provider.synthesize(
                        text=chunk,
                        voice=(
                            settings
                            .TEXT_TO_SPEECH_VOICE
                        ),
                    )
                )

        except Exception as exc:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Text-to-speech "
                    "provider failed."
                ),
            ) from exc

        return audio_chunks

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        text = re.sub(
            r"```.*?```",
            "",
            text,
            flags=re.DOTALL,
        )

        text = re.sub(
            r"`([^`]*)`",
            r"\1",
            text,
        )

        text = re.sub(
            r"!\[[^\]]*\]\([^)]*\)",
            "",
            text,
        )

        text = re.sub(
            r"\[([^\]]+)\]\([^)]*\)",
            r"\1",
            text,
        )

        text = re.sub(
            r"[*_>#~-]",
            "",
            text,
        )

        return " ".join(
            text.split()
        )

    @staticmethod
    def _split_text(
        text: str,
        max_length: int,
    ) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        chunks: list[str] = []

        current = ""

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            if len(sentence) > max_length:

                words = sentence.split()

                for word in words:

                    candidate = (
                        f"{current} {word}"
                    ).strip()

                    if (
                        len(candidate)
                        <= max_length
                    ):
                        current = candidate

                    else:

                        if current:
                            chunks.append(
                                current
                            )

                        current = word

                continue

            candidate = (
                f"{current} {sentence}"
            ).strip()

            if (
                len(candidate)
                <= max_length
            ):
                current = candidate

            else:

                if current:
                    chunks.append(
                        current
                    )

                current = sentence

        if current:
            chunks.append(current)

        return chunks