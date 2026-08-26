from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.document_repository import (
    get_document_by_id,
)
from app.services.retrieval_service import RetrievalResult


@dataclass(frozen=True)
class RAGSource:
    document_id: int
    document_name: str
    page_number: int | None


def build_rag_sources(
    db: Session,
    *,
    results: list[RetrievalResult],
    user_id: int,
) -> list[RAGSource]:

    if not results:
        return []

    sources: list[RAGSource] = []

    document_cache: dict[int, str] = {}

    seen: set[tuple[int, int | None]] = set()

    for result in results:

        source_key = (
            result.document_id,
            result.page_number,
        )

        if source_key in seen:
            continue

        seen.add(source_key)

        if result.document_id not in document_cache:

            document = get_document_by_id(
                db=db,
                document_id=result.document_id,
                user_id=user_id,
            )

            if document is None:
                continue

            document_cache[result.document_id] = (
                document.original_name
            )

        sources.append(
            RAGSource(
                document_id=result.document_id,
                document_name=document_cache[
                    result.document_id
                ],
                page_number=result.page_number,
            )
        )

    return sources


def format_rag_sources(
    sources: list[RAGSource],
) -> str:

    if not sources:
        return ""

    lines = [
        "### Sources",
        "",
    ]

    for source in sources:

        if source.page_number is None:
            lines.append(
                f"- {source.document_name}"
            )
        else:
            lines.append(
                f"- {source.document_name}, "
                f"page {source.page_number}"
            )

    return "\n".join(lines)