from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):

    @abstractmethod
    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate one embedding vector for each input text."""
        raise NotImplementedError

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        embeddings = self.embed_texts([text])

        if len(embeddings) != 1:
            raise RuntimeError(
                "Embedding provider returned an unexpected number of vectors."
            )

        return embeddings[0]