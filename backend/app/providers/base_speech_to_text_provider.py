from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseSpeechToTextProvider(ABC):

    @abstractmethod
    def transcribe(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> str:
        pass