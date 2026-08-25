from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    document_name: str
    page_number: int | None
    content: str