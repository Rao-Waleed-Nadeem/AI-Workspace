from pathlib import Path

from fastapi import HTTPException

from pypdf import PdfReader


def extract_pdf_text(
    file_path: str,
) -> dict:

    path = Path(file_path)

    try:
        reader = PdfReader(
            str(path),
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text() or ""

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the PDF document.",
        ) from exc

    full_text = "\n\n".join(
        page["text"]
        for page in pages
    )

    return {
        "page_count": len(reader.pages),
        "text": full_text,
        "pages": pages,
    }