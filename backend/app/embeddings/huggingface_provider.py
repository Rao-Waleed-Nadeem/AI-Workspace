import math

from huggingface_hub import InferenceClient

from app.core.config import settings
from app.embeddings.base import BaseEmbeddingProvider


class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):

    def __init__(self):

        if not settings.HF_TOKEN:
            raise RuntimeError(
                "HF_TOKEN is not configured."
            )

        if not settings.EMBEDDING_MODEL:
            raise RuntimeError(
                "EMBEDDING_MODEL is not configured."
            )

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=settings.HF_TOKEN,
            model=settings.EMBEDDING_MODEL,
        )

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        if any(
            not text.strip()
            for text in texts
        ):
            raise ValueError(
                "Embedding input texts must not be empty."
            )

        result = self.client.feature_extraction(
            texts,
            model=settings.EMBEDDING_MODEL,
        )

        vectors = result.tolist()

        if len(vectors) != len(texts):
            raise RuntimeError(
                "Embedding provider returned an unexpected number of vectors."
            )

        normalized_vectors: list[list[float]] = []

        for vector in vectors:

            values = [
                float(value)
                for value in vector
            ]

            norm = math.sqrt(
                sum(
                    value * value
                    for value in values
                )
            )

            if norm == 0:
                raise RuntimeError(
                    "Embedding provider returned a zero vector."
                )

            normalized_vectors.append(
                [
                    value / norm
                    for value in values
                ]
            )

        return normalized_vectors