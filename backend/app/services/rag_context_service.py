from dataclasses import dataclass


MAX_CHUNK_CHARACTERS = 2500
MAX_CONTEXT_CHARACTERS = 6000


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
    total_characters = 0

    for chunk in chunks:

        content = chunk.content.strip()

        if not content:
            continue

        if len(content) > MAX_CHUNK_CHARACTERS:
            content = content[:MAX_CHUNK_CHARACTERS].rstrip()

        source = f"Document ID: {chunk.document_id}"

        if chunk.page_number is not None:
            source += f" | Page {chunk.page_number}"

        section = (
            f"[Source: {source}]\n"
            f"{content}"
        )

        section_length = len(section)

        if (
            total_characters + section_length
            > MAX_CONTEXT_CHARACTERS
        ):
            remaining = (
                MAX_CONTEXT_CHARACTERS
                - total_characters
            )

            if remaining <= 0:
                break

            section = section[:remaining]

        sections.append(section)

        total_characters += len(section)

        if total_characters >= MAX_CONTEXT_CHARACTERS:
            break

    return "\n\n---\n\n".join(sections)