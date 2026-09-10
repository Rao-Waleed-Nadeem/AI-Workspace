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


def get_user_memories(
    db: Session,
    user_id: int,
    limit: int = 50,
) -> list[Memory]:

    return (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
        )
        .order_by(
            Memory.updated_at.desc(),
        )
        .limit(limit)
        .all()
    )


def delete_memory(
    db: Session,
    user_id: int,
    memory_id: int,
) -> bool:

    memory = (
        db.query(Memory)
        .filter(
            Memory.id == memory_id,
            Memory.user_id == user_id,
        )
        .first()
    )

    if memory is None:
        return False

    db.delete(memory)

    return True


def delete_all_memories(
    db: Session,
    user_id: int,
) -> int:

    memories = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
        )
        .all()
    )

    count = len(memories)

    for memory in memories:
        db.delete(memory)

    return count