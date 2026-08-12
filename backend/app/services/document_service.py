from pathlib import Path
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.config import settings
from app.repositories.document_repository import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_by_user,
)
from app.services.file_upload_service import (
    save_document_upload,
)
from app.utils.pdf_extractor import (
    extract_pdf_text,
)


async def process_document_upload(
    db: Session,
    file: UploadFile,
    user_id: int,
):

    uploaded_file = await save_document_upload(
        file,
    )

    temporary_path = Path(
        uploaded_file["storage_path"],
    )

    try:
        extracted = extract_pdf_text(
            str(temporary_path),
        )

        document_dir = Path(
            settings.DOCUMENT_UPLOAD_DIR,
        )

        document_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        final_path = (
            document_dir
            / uploaded_file["storage_name"]
        )

        shutil.move(
            str(temporary_path),
            str(final_path),
        )

        document = create_document(
            db=db,
            user_id=user_id,
            original_name=uploaded_file[
                "original_name"
            ],
            mime_type=uploaded_file[
                "mime_type"
            ],
            storage_path=str(final_path),
            size=uploaded_file["size"],
            page_count=extracted[
                "page_count"
            ],
            extracted_text=extracted["text"],
        )

        db.commit()

        return document

    except Exception:
        db.rollback()

        if temporary_path.exists():
            temporary_path.unlink()

        raise


def list_user_documents(
    db: Session,
    user_id: int,
):

    return get_documents_by_user(
        db=db,
        user_id=user_id,
    )

def get_user_document(
    db: Session,
    document_id: int,
    user_id: int,
):

    document = get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document

def remove_user_document(
    db: Session,
    document_id: int,
    user_id: int,
):

    document = get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    storage_path = Path(
        document.storage_path,
    )

    delete_document(
        db=db,
        document=document,
    )

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    if storage_path.exists():
        storage_path.unlink()

        