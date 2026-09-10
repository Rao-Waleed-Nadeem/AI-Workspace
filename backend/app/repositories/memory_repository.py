from sqlalchemy.orm import Session

from app.models import Memory


def create_memory(
    db: Session,
    user_id: int,
    key: str,
    value: str,
) -> Memory:

    memory = Memory(
        user_id=user_id,
        key=key,
        value=value,
    )

    db.add(memory)
    db.flush()
    db.refresh(memory)

    return memory


def get_memory_by_key(
    db: Session,
    user_id: int,
    key: str,
) -> Memory | None:

    return (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.key == key,
        )
        .first()
    )