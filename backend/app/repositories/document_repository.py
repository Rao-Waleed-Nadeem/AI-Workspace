from sqlalchemy.orm import Session

from app.models import Document


def create_document(
    db: Session,
    user_id: int,
    original_name: str,
    mime_type: str,
    storage_path: str,
    size: int,
    page_count: int,
    extracted_text: str,
) -> Document:

    document = Document(
        user_id=user_id,
        original_name=original_name,
        mime_type=mime_type,
        storage_path=storage_path,
        size=size,
        page_count=page_count,
        extracted_text=extracted_text,
    )

    db.add(document)
    db.flush()
    db.refresh(document)

    return document