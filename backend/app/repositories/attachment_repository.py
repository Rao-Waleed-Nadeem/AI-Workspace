from sqlalchemy.orm import Session
from app.models import Message

from app.models import Attachment

def create_attachment(
    db: Session,
    message_id: int,
    attachment_type: str,
    mime_type: str,
    original_name: str,
    storage_path: str,
    size: int,
) -> Attachment:

    attachment = Attachment(
        message_id=message_id,
        attachment_type=attachment_type,
        mime_type=mime_type,
        original_name=original_name,
        storage_path=storage_path,
        size=size,
    )

    db.add(attachment)

    db.flush()

    db.refresh(attachment)

    return attachment

def get_message_attachments(
    db: Session,
    message_id: int,
) -> list[Attachment]:

    return (
        db.query(Attachment)
        .filter(
            Attachment.message_id == message_id,
        )
        .order_by(
            Attachment.created_at.asc(),
        )
        .all()
    )

def delete_attachment(
    db: Session,
    attachment_id: int,
):

    attachment = (
        db.query(Attachment)
        .filter(
            Attachment.id == attachment_id,
        )
        .first()
    )

    if attachment:

        db.delete(attachment)

    return attachment

def delete_message_attachments(
    db: Session,
    message_id: int,
):

    (
        db.query(Attachment)
        .filter(
            Attachment.message_id == message_id,
        )
        .delete()
    )

def get_attachment(
    db: Session,
    attachment_id: int,
):

    return (
        db.query(Attachment)
        .filter(
            Attachment.id == attachment_id,
        )
        .first()
    )

def get_chat_attachments(
    db: Session,
    chat_id: int,
):

    return (
        db.query(Attachment)
        .join(Attachment.message)
        .filter(
            Message.chat_id == chat_id,
        )
        .all()
    )