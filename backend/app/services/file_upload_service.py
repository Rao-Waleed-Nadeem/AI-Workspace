from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.utils.document_validator import (
    sanitize_filename,
    validate_content_type,
    validate_extension,
    validate_pdf_signature,
    validate_size,
)


CHUNK_SIZE = 1024 * 1024


async def save_document_upload(
    file: UploadFile,
) -> dict:

    original_name = sanitize_filename(
        file.filename,
    )

    validate_extension(
        original_name,
    )

    validate_content_type(
        file.content_type,
    )

    await validate_pdf_signature(
        file,
    )

    upload_dir = Path(
        settings.TEMP_UPLOAD_DIR,
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    storage_name = f"{uuid4()}.pdf"

    storage_path = upload_dir / storage_name

    total_size = 0

    try:
        with storage_path.open("wb") as destination:

            while True:
                chunk = await file.read(
                    CHUNK_SIZE,
                )

                if not chunk:
                    break

                total_size += len(chunk)

                validate_size(
                    total_size,
                )

                destination.write(chunk)

    except Exception:
        if storage_path.exists():
            storage_path.unlink()

        raise

    finally:
        await file.close()

    return {
        "original_name": original_name,
        "storage_name": storage_name,
        "storage_path": str(storage_path),
        "mime_type": file.content_type,
        "size": total_size,
    }