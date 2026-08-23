from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int
    page_number: int | None = None


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def _normalize_text(
    text: str,
) -> str:

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


def _split_long_sentence(
    sentence: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Split a sentence that is longer than chunk_size.

    The split attempts to happen at word boundaries and
    preserves the configured overlap between pieces.
    """

    words = sentence.split()

    if not words:
        return []

    pieces: list[str] = []
    current_words: list[str] = []

    for word in words:

        candidate = (
            word
            if not current_words
            else f"{' '.join(current_words)} {word}"
        )

        if len(candidate) <= chunk_size:
            current_words.append(word)
            continue

        if current_words:
            piece = " ".join(current_words)

            pieces.append(
                piece,
            )

            overlap_words: list[str] = []
            overlap_length = 0

            for overlap_word in reversed(
                current_words,
            ):

                additional_length = (
                    len(overlap_word)
                    if not overlap_words
                    else len(overlap_word) + 1
                )

                if (
                    overlap_length
                    + additional_length
                    > chunk_overlap
                ):
                    break

                overlap_words.insert(
                    0,
                    overlap_word,
                )

                overlap_length += additional_length

            current_words = (
                overlap_words
                + [word]
            )

        else:
            # Handles a single word longer than chunk_size.
            start = 0

            while start < len(word):

                end = min(
                    start + chunk_size,
                    len(word),
                )

                pieces.append(
                    word[start:end],
                )

                if end >= len(word):
                    break

                start = max(
                    start + 1,
                    end - chunk_overlap,
                )

            current_words = []

    if current_words:
        pieces.append(
            " ".join(current_words),
        )

    return pieces


def _build_units(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:

    paragraphs = _split_paragraphs(
        text,
    )

    units: list[str] = []

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:
            units.append(
                paragraph,
            )
            continue

        sentences = _split_sentences(
            paragraph,
        )

        for sentence in sentences:

            if len(sentence) <= chunk_size:
                units.append(
                    sentence,
                )
                continue

            units.extend(
                _split_long_sentence(
                    sentence=sentence,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
            )

    return units


def _get_overlap_text(
    text: str,
    chunk_overlap: int,
) -> str:
    """
    Return an overlap from the end of the current chunk.

    The overlap is selected by complete words instead of
    cutting the text at an arbitrary character boundary.
    """

    words = text.split()

    if not words:
        return ""

    overlap_words: list[str] = []
    overlap_length = 0

    for word in reversed(words):

        additional_length = (
            len(word)
            if not overlap_words
            else len(word) + 1
        )

        if (
            overlap_length
            + additional_length
            > chunk_overlap
        ):
            break

        overlap_words.insert(
            0,
            word,
        )

        overlap_length += additional_length

    return " ".join(
        overlap_words,
    )


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
        text=normalized_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
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

            overlap_text = _get_overlap_text(
                text=current_text,
                chunk_overlap=chunk_overlap,
            )

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


def chunk_pages(
    pages: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:
    """
    Split page-level PDF text into chunks while preserving
    the originating page number.
    """

    _validate_chunk_configuration(
        chunk_size,
        chunk_overlap,
    )

    chunks: list[TextChunk] = []

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        page_chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for page_chunk in page_chunks:

            chunks.append(
                TextChunk(
                    text=page_chunk.text,
                    chunk_index=len(chunks),
                    page_number=page_number,
                )
            )

    return chunks