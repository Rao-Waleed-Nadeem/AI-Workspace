import os
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.generated_image import GeneratedImage
from app.models.user import User
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
    db: Session = Depends(get_db),
):

    service = ImageGenerationService()

    generated_image = service.generate(
        db=db,
        user_id=current_user.id,
        user_prompt=request.prompt,
    )

    return ImageGenerationResponse(
        id=generated_image.id,
        url=f"/images/{generated_image.id}",
        expires_at=generated_image.expires_at,
    )


@router.get("/{image_id}")
def get_generated_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    image = (
        db.query(GeneratedImage)
        .filter(
            GeneratedImage.id == image_id,
            GeneratedImage.user_id == current_user.id,
        )
        .first()
    )

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    now = datetime.now(timezone.utc)

    if image.expires_at <= now:

        if os.path.exists(image.storage_path):
            os.remove(image.storage_path)

        db.delete(image)
        db.commit()

        raise HTTPException(
            status_code=404,
            detail="Image has expired",
        )

    if not os.path.exists(image.storage_path):
        raise HTTPException(
            status_code=404,
            detail="Image file not found",
        )

    return FileResponse(
        image.storage_path,
        media_type="image/png",
        filename=f"generated-{image.id}.png",
    )