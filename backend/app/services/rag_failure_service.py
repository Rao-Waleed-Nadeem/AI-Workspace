from app.services.rag_exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    InsufficientContextError,
    NoRelevantContextError,
    UnsupportedDocumentError,
)


def get_rag_failure_message(
    error: Exception,
) -> str:

    if isinstance(
        error,
        DocumentNotFoundError,
    ):
        return (
            "The selected document could not be found."
        )

    if isinstance(
        error,
        UnsupportedDocumentError,
    ):
        return (
            "This document type is not supported "
            "for document question answering."
        )

    if isinstance(
        error,
        EmptyDocumentError,
    ):
        return (
            "The selected document does not contain "
            "usable extracted text."
        )

    if isinstance(
        error,
        NoRelevantContextError,
    ):
        return (
            "I couldn't find relevant information "
            "in the selected document to answer this question."
        )

    if isinstance(
        error,
        InsufficientContextError,
    ):
        return (
            "The selected document does not contain "
            "enough information to answer this question reliably."
        )

    return (
        "I couldn't answer the question using the selected document."
    )