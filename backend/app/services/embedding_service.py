from dataclasses import dataclass

from app.embeddings.base import BaseEmbeddingProvider
from app.embeddings.factory import get_embedding_provider
from app.utils.text_chunker import (
    TextChunk,
    chunk_text,
)


@dataclass(frozen=True)
class EmbeddedChunk:

    chunk: TextChunk
    embedding: list[float]


class EmbeddingService:

    def __init__(
        self,
        provider: BaseEmbeddingProvider | None = None,
    ):
        self.provider = (
            provider
            or get_embedding_provider()
        )

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return self.provider.embed_text(
            text,
        )

    def embed_chunks(
        self,
        chunks: list[TextChunk],
    ) -> list[EmbeddedChunk]:

        if not chunks:
            return []

        texts = [
            chunk.text
            for chunk in chunks
        ]

        vectors = self.provider.embed_texts(
            texts,
        )

        if len(vectors) != len(chunks):
            raise RuntimeError(
                "Embedding count does not match chunk count."
            )

        return [
            EmbeddedChunk(
                chunk=chunk,
                embedding=vector,
            )
            for chunk, vector in zip(
                chunks,
                vectors,
            )
        ]

    def embed_document_text(
        self,
        extracted_text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> list[EmbeddedChunk]:

        chunks = chunk_text(
            extracted_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return self.embed_chunks(
            chunks,
        )