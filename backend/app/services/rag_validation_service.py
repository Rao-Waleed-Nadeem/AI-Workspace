from sqlalchemy.orm import Session

from app.repositories.document_repository import (
    get_document_by_id,
)

from app.services.rag_exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    InsufficientContextError,
    NoRelevantContextError,
    UnsupportedDocumentError,
)

from app.services.retrieval_service import RetrievalResult


SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".pdf",
}

MIN_RELEVANT_CHUNKS = 1


def validate_document_for_rag(
    db: Session,
    *,
    document_id: int,
    user_id: int,
):
    document = get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    if document is None:
        raise DocumentNotFoundError(
            "Document not found."
        )

    document_name = document.original_name or ""

    extension = ""

    if "." in document_name:
        extension = (
            "."
            + document_name.rsplit(".", 1)[1].lower()
        )

    if extension not in SUPPORTED_DOCUMENT_EXTENSIONS:
        raise UnsupportedDocumentError(
            "This document type is not supported for RAG."
        )

    return document


def validate_retrieval_results(
    results: list[RetrievalResult],
) -> None:

    if not results:
        raise NoRelevantContextError(
            "No relevant information was found "
            "in the selected document."
        )

    usable_results = [
        result
        for result in results
        if result.content.strip()
    ]

    if not usable_results:
        raise EmptyDocumentError(
            "The selected document contains no usable text."
        )

    if len(usable_results) < MIN_RELEVANT_CHUNKS:
        raise InsufficientContextError(
            "There is not enough relevant information "
            "to answer this question reliably."
        )