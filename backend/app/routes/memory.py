from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.database import get_db

from app.core.dependencies import get_current_user
from app.models import User
from app.providers.groq_provider import GroqProvider

from app.services.memory_extraction_service import (
    MemoryExtractionError,
    MemoryExtractionService,
)

from app.schemas.memory import (
    MemoryExtractionResponse,
    MemoryResponse,
)
from app.services.memory_service import MemoryService

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


provider = GroqProvider()

memory_service = MemoryService()

memory_extraction_service = (
    MemoryExtractionService(
        provider=provider,
    )
)


class MemoryExtractionRequest(BaseModel):
    message: str


@router.post(
    "/extract",
    response_model=MemoryExtractionResponse,
)
def extract_memories(
    request: MemoryExtractionRequest,
    current_user: User = Depends(
        get_current_user,
    ),
):

    try:

        memories = (
            memory_extraction_service.extract(
                message=request.message,
            )
        )

    except MemoryExtractionError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return MemoryExtractionResponse(
        memories=memories,
    )

@router.get(
    "",
    response_model=list[MemoryResponse],
)
def list_memories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return memory_service.list_memories(
        db=db,
        user_id=current_user.id,
    )

@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = memory_service.remove_memory(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found",
        )

    db.commit()

    return None

@router.delete(
    "",
)
def clear_memories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_count = memory_service.clear_memories(
        db=db,
        user_id=current_user.id,
    )

    db.commit()

    return {
        "deleted_count": deleted_count,
    }