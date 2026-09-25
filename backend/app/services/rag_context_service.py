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

    separator = "\n\n---\n\n"

    sections: list[str] = []
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

        prefix = f"[Source: {source}]\n"

        remaining = MAX_CONTEXT_CHARACTERS - total_characters

        separator_cost = len(separator) if sections else 0

        if remaining <= separator_cost + len(prefix):
            break

        available_content = remaining - separator_cost - len(prefix)

        content = content[:available_content].rstrip()

        if not content:
            break

        section = prefix + content

        sections.append(section)

        total_characters += separator_cost + len(section)

        if total_characters >= MAX_CONTEXT_CHARACTERS:
            break

    return separator.join(sections)
