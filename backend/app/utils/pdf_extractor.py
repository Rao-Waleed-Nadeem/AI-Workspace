from pathlib import Path

from fastapi import HTTPException
from pypdf import PdfReader


def extract_pdf_text(
    file_path: str,
) -> dict:

    path = Path(file_path)

    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail="Stored PDF file could not be found.",
        )

    try:
        reader = PdfReader(
            str(path),
        )

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            pages.append(
                text,
            )

        extracted_text = "\n\n".join(
            pages,
        ).strip()

        return {
            "text": extracted_text,
            "page_count": len(reader.pages),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="The uploaded PDF could not be processed.",
        ) from exc