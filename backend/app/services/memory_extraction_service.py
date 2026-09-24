import json

from pydantic import ValidationError

from app.providers.base_provider import BaseAIProvider
from app.prompts.memory import build_memory_extraction_prompt
from app.schemas.memory import (
    MemoryCandidate,
    MemoryExtractionResponse,
)

EXCLUDED_MEMORY_KEYS = {
    "language",
    "preferred_language",
    "response_language",
}


class MemoryExtractionError(Exception):
    """Raised when AI returns invalid memory extraction data."""


class MemoryExtractionService:

    def __init__(
        self,
        provider: BaseAIProvider,
    ):
        self.provider = provider

    def extract(
        self,
        message: str,
    ) -> list[MemoryCandidate]:

        message = message.strip()

        if not message:
            return []

        prompt = build_memory_extraction_prompt(
            message,
        )

        try:
            raw_response = (
                self.provider.generate_structured_response(
                    [
                        {
                            "role": "system",
                            "content": (
                                "Return only valid JSON. "
                                "Do not include Markdown, "
                                "explanations, or extra fields."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ]
                )
            )
        except Exception as exc:
            raise MemoryExtractionError(
                "Memory extraction model failed to produce JSON."
            ) from exc

        try:
            payload = json.loads(raw_response)
            result = MemoryExtractionResponse.model_validate(payload)
        except (
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ) as exc:
            raise MemoryExtractionError(
                "AI returned an invalid memory extraction response."
            ) from exc

        return self._sanitize_candidates(
            result.memories,
        )

    @staticmethod
    def _sanitize_candidates(
        candidates: list[MemoryCandidate],
    ) -> list[MemoryCandidate]:

        sanitized = []
        seen_keys = set()

        for candidate in candidates:

            key = candidate.key.strip().lower()
            value = candidate.value.strip()

            if (
                not key
                or not value
                or key in seen_keys
                or key in EXCLUDED_MEMORY_KEYS
            ):
                continue

            sanitized.append(
                MemoryCandidate(
                    key=key,
                    value=value,
                )
            )

            seen_keys.add(key)

        return sanitized
