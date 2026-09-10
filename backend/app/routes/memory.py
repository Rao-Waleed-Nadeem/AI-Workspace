from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.models import User
from app.providers.groq_provider import GroqProvider
from app.schemas.memory import (
    MemoryExtractionResponse,
)
from app.services.memory_extraction_service import (
    MemoryExtractionError,
    MemoryExtractionService,
)


router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


provider = GroqProvider()

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