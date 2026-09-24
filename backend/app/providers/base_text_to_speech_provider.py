from abc import ABC, abstractmethod


class BaseTextToSpeechProvider(ABC):

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str,
    ) -> bytes:
        pass