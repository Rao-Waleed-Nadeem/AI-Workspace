class RAGError(Exception):
    """Base exception for RAG-specific failures."""


class DocumentNotFoundError(RAGError):
    """The requested document does not exist or is not owned by the user."""


class UnsupportedDocumentError(RAGError):
    """The requested document type is not supported by RAG."""


class EmptyDocumentError(RAGError):
    """The document exists but contains no usable extracted content."""


class NoRelevantContextError(RAGError):
    """No retrieved chunks meet the relevance threshold."""


class InsufficientContextError(RAGError):
    """Retrieved evidence is not sufficient for reliable answering."""