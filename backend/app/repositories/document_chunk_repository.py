from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.document_chunk import DocumentChunk


def create_document_chunks(
    db: Session,
    *,
    document_id: int,
    user_id: int,
    chunks: list[dict],
    embedding_model: str,
) -> list[DocumentChunk]:
    document_chunks = []

    for chunk in chunks:
        document_chunk = DocumentChunk(
            document_id=document_id,
            user_id=user_id,
            chunk_index=chunk["chunk_index"],
            page_number=chunk.get("page_number"),
            content=chunk["text"],
            embedding_model=embedding_model,
            embedding=chunk["embedding"],
        )

        db.add(document_chunk)
        document_chunks.append(document_chunk)

    db.flush()

    return document_chunks




def search_similar_chunks(
    db: Session,
    *,
    query_embedding: list[float],
    user_id: int,
    document_id: int | None = None,
    limit: int = 5,
) -> list[tuple[DocumentChunk, float]]:

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding,
    )

    similarity = (
        1 - distance
    ).label(
        "similarity",
    )

    statement = (
        select(
            DocumentChunk,
            similarity,
        )
        .where(
            DocumentChunk.user_id == user_id,
        )
        .order_by(
            distance,
        )
        .limit(
            limit,
        )
    )

    if document_id is not None:
        statement = statement.where(
            DocumentChunk.document_id == document_id,
        )

    return list(
        db.execute(
            statement,
        ).all()
    )