from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.document_chunk_repository import (
    search_similar_chunks,
)
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: int
    document_id: int
    user_id: int
    chunk_index: int
    page_number: int | None
    content: str
    similarity: float


class RetrievalService:

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

    def retrieve(
        self,
        db: Session,
        *,
        question: str,
        user_id: int,
        document_id: int | None = None,
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        question = question.strip()

        if not question:
            raise ValueError(
                "Retrieval question cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_embedding = (
            self.embedding_service.embed_text(
                question,
            )
        )

        results = search_similar_chunks(
            db=db,
            query_embedding=query_embedding,
            user_id=user_id,
            document_id=document_id,
            limit=top_k,
        )

        return [
            RetrievalResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                user_id=chunk.user_id,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                content=chunk.content,
                similarity=float(similarity),
            )
            for chunk, similarity in results
        ]