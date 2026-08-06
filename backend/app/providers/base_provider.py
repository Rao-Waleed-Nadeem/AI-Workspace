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

        pass