from pathlib import Path
import re
import unicodedata

from fastapi import HTTPException, UploadFile

from app.core.config import settings


ALLOWED_EXTENSIONS = {
    ".pdf",
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
}

PDF_SIGNATURE = b"%PDF-"


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    filename = unicodedata.normalize(
        "NFKC",
        filename,
    )

    filename = Path(filename).name

    filename = re.sub(
        r"[^A-Za-z0-9._ -]",
        "_",
        filename,
    )

    filename = filename.strip(" .")

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    return filename


def validate_extension(filename: str) -> None:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported.",
        )


def validate_content_type(
    content_type: str | None,
) -> None:

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="The uploaded file must have MIME type application/pdf.",
        )


async def validate_pdf_signature(
    file: UploadFile,
) -> None:

    await file.seek(0)

    signature = await file.read(
        len(PDF_SIGNATURE)
    )

    await file.seek(0)

    if signature != PDF_SIGNATURE:
        raise HTTPException(
            status_code=415,
            detail="The uploaded file is not a valid PDF.",
        )


def validate_size(size: int) -> None:
    if size > settings.MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Document exceeds the maximum allowed size.",
        )