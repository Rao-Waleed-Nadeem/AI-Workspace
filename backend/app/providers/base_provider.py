from abc import ABC, abstractmethod
from app.core.config import settings


class BaseAIProvider(ABC):

    @abstractmethod
    def generate_response(
        self,
        messages: list[dict],
    ) -> str:
        pass

    @abstractmethod
    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        pass

    @abstractmethod
    def generate_vision_response(
        self,
        messages: list[dict],
    ) -> str:

        completion = self.client.chat.completions.create(
            model=settings.VISION_MODEL_NAME,
            messages=messages,
        )

        return completion.choices[0].message.content