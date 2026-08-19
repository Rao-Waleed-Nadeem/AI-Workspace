from sqlalchemy.orm import Session

from app.repositories.document_chunk_repository import (
    search_similar_chunks,
)
from app.services.embedding_service import EmbeddingService


class SemanticSearchService:

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

    def search(
        self,
        db: Session,
        *,
        question: str,
        limit: int = 5,
    ):

        if not question.strip():
            raise ValueError(
                "Search question cannot be empty."
            )

        query_embedding = (
            self.embedding_service.embed_text(
                question,
            )
        )

        return search_similar_chunks(
            db=db,
            query_embedding=query_embedding,
            limit=limit,
        )