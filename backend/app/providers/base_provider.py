from abc import ABC, abstractmethod


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