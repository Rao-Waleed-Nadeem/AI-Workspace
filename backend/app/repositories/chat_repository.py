from sqlalchemy.orm import Session

from app.models import Chat


def create_chat(
    db: Session,
    title: str,
) -> Chat:

    chat = Chat(
        title=title,
    )

    db.add(chat)

    db.flush()

    db.refresh(chat)

    return chat


def get_chat(
    db: Session,
    chat_id: int,
) -> Chat | None:

    return db.query(Chat).filter(Chat.id == chat_id).first()


def get_all_chats(
    db: Session,
):

    return db.query(Chat).order_by(Chat.created_at.desc()).all()


def delete_chat(
    db: Session,
    chat: Chat,
):

    db.delete(chat)

    db.commit()
