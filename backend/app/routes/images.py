from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.image_generation import (
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from app.services.image_generation_service import (
    ImageGenerationService,
)


router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


@router.post(
    "/generate",
    response_model=ImageGenerationResponse,
)
def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
):

    service = ImageGenerationService()

    result = service.generate(
        user_prompt=request.prompt,
    )

    return ImageGenerationResponse(
        image=result.b64_json,
    )