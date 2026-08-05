from sqlalchemy.orm import Session

from app.models import Chat


def create_chat(
    db: Session,
    title: str,
    user_id: int,
) -> Chat:

    chat = Chat(
        title=title,
        user_id=user_id,
    )

    db.add(chat)

    db.flush()

    db.refresh(chat)

    return chat


def get_chat(
    db: Session,
    chat_id: int,
    user_id: int,
) -> Chat | None:

    return db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()


def get_all_chats(
    db: Session,
    user_id: int,
):

    return db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()


def delete_chat(
    db: Session,
    chat_id: int,
    user_id: int,
) -> bool:

    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == user_id,
        )
        .first()
    )

    if chat is None:
        return False

    db.delete(chat)
    db.commit()

    return True