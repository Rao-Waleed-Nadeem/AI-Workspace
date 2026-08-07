from sqlalchemy.orm import Session, joinedload

from app.models import Message, Chat


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
    user_id: int,
):

    return (
        db.query(Message)
        .options(joinedload(Message.attachments))
        .join(Chat, Message.chat_id == Chat.id)
        .filter(
            Message.chat_id == chat_id,
            Chat.user_id == user_id,
        )
        .order_by(Message.id.asc())
        .all()
    )
