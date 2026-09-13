from app.prompts.image_generation import build_image_prompt
from app.providers.huggingface_image_generation_provider import (
    HuggingFaceImageGenerationProvider,
)
from app.providers.image_generation import GeneratedImage


class ImageGenerationService:

    def __init__(self):
        self.provider = HuggingFaceImageGenerationProvider()

    def generate(
        self,
        user_prompt: str,
    ) -> GeneratedImage:

        final_prompt = build_image_prompt(
            user_prompt
        )

        return self.provider.generate_image(
            final_prompt
        )