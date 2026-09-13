from abc import ABC, abstractmethod

from app.providers.image_generation import GeneratedImage


class BaseImageGenerationProvider(ABC):

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
    ) -> GeneratedImage:
        pass