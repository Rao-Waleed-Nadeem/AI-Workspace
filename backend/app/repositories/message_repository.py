from sqlalchemy.orm import Session

from app.models import Message


def create_message(
    db: Session,
    chat_id: int,
    role: str,
    content: str,
) -> Message:

    message = Message(
        chat_id=chat_id,
        role=role,
        content=content,
    )

    db.add(message)

    db.flush()

    db.refresh(message)

    return message


def get_chat_messages(
    db: Session,
    chat_id: int,
):

    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .all()
    )
