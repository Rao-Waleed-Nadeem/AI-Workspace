from app.providers.base_provider import BaseAIProvider
from app.providers.groq_provider import GroqProvider


def create_ai_provider() -> BaseAIProvider:
    """Return the configured text/multimodal AI provider."""
    return GroqProvider()