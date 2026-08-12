from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings


CHUNK_SIZE = 1024 * 1024


async def save_temporary_upload(
    file: UploadFile,
) -> dict:

    upload_dir = Path(settings.UPLOAD_DIR)

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    storage_name = str(uuid4())

    storage_path = upload_dir / storage_name

    total_size = 0

    try:
        with storage_path.open("wb") as destination:

            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Uploaded file exceeds the maximum allowed size.",
                    )

                destination.write(chunk)

    except Exception:
        if storage_path.exists():
            storage_path.unlink()

        raise

    finally:
        await file.close()

    return {
        "storage_name": storage_name,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": total_size,
        "storage_path": str(storage_path),
    }