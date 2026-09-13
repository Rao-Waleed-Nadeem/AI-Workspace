import base64
import os
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.generated_image import GeneratedImage
from app.prompts.image_generation import build_image_prompt
from app.providers.huggingface_image_generation_provider import (
    HuggingFaceImageGenerationProvider,
)


class ImageGenerationService:

    def __init__(self):
        self.provider = HuggingFaceImageGenerationProvider()

    def generate(
        self,
        db: Session,
        user_id: int,
        user_prompt: str,
    ) -> GeneratedImage:

        final_prompt = build_image_prompt(
            user_prompt
        )

        result = self.provider.generate_image(
            final_prompt
        )

        image_bytes = base64.b64decode(
            result.b64_json
        )

        user_directory = os.path.join(
            settings.GENERATED_IMAGE_DIR,
            str(user_id),
        )

        os.makedirs(
            user_directory,
            exist_ok=True,
        )

        filename = f"{uuid.uuid4()}.png"

        relative_path = os.path.join(
            user_directory,
            filename,
        )

        with open(
            relative_path,
            "wb",
        ) as image_file:

            image_file.write(
                image_bytes
            )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                hours=settings.GENERATED_IMAGE_EXPIRATION_HOURS
            )
        )

        generated_image = GeneratedImage(
            user_id=user_id,
            prompt=user_prompt,
            storage_path=relative_path,
            expires_at=expires_at,
        )

        db.add(generated_image)
        db.commit()
        db.refresh(generated_image)

        return generated_image