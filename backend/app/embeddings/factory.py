from app.core.config import settings
from app.embeddings.base import BaseEmbeddingProvider
from app.embeddings.huggingface_provider import (
    HuggingFaceEmbeddingProvider,
)


def get_embedding_provider() -> BaseEmbeddingProvider:

    if settings.EMBEDDING_PROVIDER == "huggingface":
        return HuggingFaceEmbeddingProvider()

    raise RuntimeError(
        f"Unsupported embedding provider: "
        f"{settings.EMBEDDING_PROVIDER}"
    )