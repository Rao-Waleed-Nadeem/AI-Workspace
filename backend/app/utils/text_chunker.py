from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def _normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _validate_chunk_configuration(
    chunk_size: int,
    chunk_overlap: int,
) -> None:

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )


def _split_paragraphs(
    text: str,
) -> list[str]:

    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def _split_sentences(
    text: str,
) -> list[str]:

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _build_units(
    text: str,
    chunk_size: int,
) -> list[str]:

    paragraphs = _split_paragraphs(
        text,
    )

    units: list[str] = []

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:
            units.append(paragraph)
            continue

        sentences = _split_sentences(
            paragraph,
        )

        for sentence in sentences:

            if len(sentence) <= chunk_size:
                units.append(sentence)
                continue

            start = 0

            while start < len(sentence):

                end = min(
                    start + chunk_size,
                    len(sentence),
                )

                units.append(
                    sentence[start:end].strip()
                )

                start = end

    return units


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:

    _validate_chunk_configuration(
        chunk_size,
        chunk_overlap,
    )

    normalized_text = _normalize_text(
        text,
    )

    if not normalized_text:
        return []

    units = _build_units(
        normalized_text,
        chunk_size,
    )

    chunks: list[TextChunk] = []

    current_text = ""

    for unit in units:

        candidate = (
            unit
            if not current_text
            else f"{current_text} {unit}"
        )

        if len(candidate) <= chunk_size:

            current_text = candidate
            continue

        if current_text:

            chunks.append(
                TextChunk(
                    text=current_text,
                    chunk_index=len(chunks),
                )
            )

            overlap_text = current_text[
                max(
                    0,
                    len(current_text)
                    - chunk_overlap,
                ):
            ]

            current_text = (
                f"{overlap_text} {unit}".strip()
            )

        else:

            current_text = unit

    if current_text:

        chunks.append(
            TextChunk(
                text=current_text,
                chunk_index=len(chunks),
            )
        )

    return chunks