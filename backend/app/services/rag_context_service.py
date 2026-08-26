from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: int
    page_number: int | None
    content: str

def build_rag_context(
    chunks: list[RetrievedChunk],
) -> str:

    if not chunks:
        return ""

    sections = []

    for chunk in chunks:

        source = f"Document ID: {chunk.document_id}"

        if chunk.page_number is not None:
            source += f" | Page {chunk.page_number}"

        sections.append(
            f"[Source: {source}]\n"
            f"{chunk.content}"
        )

    return "\n\n---\n\n".join(sections)