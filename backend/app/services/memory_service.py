from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.memory_repository import (
    delete_all_memories,
    delete_memory,
    get_user_memories,
)


class MemoryService:

    def get_relevant_memories(
        self,
        db: Session,
        user_id: int,
    ):

        return get_user_memories(
            db=db,
            user_id=user_id,
            limit=settings.MEMORY_MAX_ITEMS,
        )

    def list_memories(
        self,
        db: Session,
        user_id: int,
    ):

        return get_user_memories(
            db=db,
            user_id=user_id,
            limit=100,
        )

    def remove_memory(
        self,
        db: Session,
        user_id: int,
        memory_id: int,
    ) -> bool:

        return delete_memory(
            db=db,
            user_id=user_id,
            memory_id=memory_id,
        )

    def clear_memories(
        self,
        db: Session,
        user_id: int,
    ) -> int:

        return delete_all_memories(
            db=db,
            user_id=user_id,
        )

    @staticmethod
    def build_memory_context(
        memories,
    ) -> str:

        if not memories:
            return ""

        lines = [
            "The following are persistent preferences or facts "
            "the user has explicitly allowed the assistant to remember:"
        ]

        for memory in memories:
            lines.append(
                f"- {memory.key}: {memory.value}"
            )

        lines.append(
            "Use these memories only when they are relevant to "
            "the current request. Do not mention the memory system "
            "unless the user asks about it."
        )

        return "\n".join(lines)