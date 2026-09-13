import base64
from io import BytesIO

from huggingface_hub import InferenceClient

from app.core.config import settings
from app.providers.base_image_generation_provider import (
    BaseImageGenerationProvider,
)
from app.providers.image_generation import GeneratedImage


class HuggingFaceImageGenerationProvider(
    BaseImageGenerationProvider
):

    def __init__(self):
        self.client = InferenceClient(
            api_key=settings.HF_TOKEN,
        )

    def generate_image(
        self,
        prompt: str,
    ) -> GeneratedImage:

        image = self.client.text_to_image(
            prompt=prompt,
            model=settings.IMAGE_MODEL_NAME,
        )

        buffer = BytesIO()

        image.save(
            buffer,
            format="PNG",
        )

        image_bytes = buffer.getvalue()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        return GeneratedImage(
            b64_json=encoded_image,
        )