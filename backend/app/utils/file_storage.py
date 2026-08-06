from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


UPLOAD_DIR = Path("uploads/images")


async def save_uploaded_file(
    image: UploadFile,
):

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = Path(
        image.filename,
    ).suffix

    filename = f"{uuid4()}{extension}"

    filepath = UPLOAD_DIR / filename

    contents = await image.read()

    with open(
        filepath,
        "wb",
    ) as file:

        file.write(contents)

    await image.seek(0)

    return {
        "attachment_type": "image",
        "original_name": image.filename,
        "mime_type": image.content_type,
        "storage_path": str(filepath),
        "size": len(contents),
    }