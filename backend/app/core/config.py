from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME")
        self.JWT_SECRET = os.getenv("JWT_SECRET")

        self.DOCUMENT_UPLOAD_DIR = os.getenv(
            "DOCUMENT_UPLOAD_DIR",
            "uploads/documents",
        )

        self.TEMP_UPLOAD_DIR = os.getenv(
            "TEMP_UPLOAD_DIR",
            "uploads/temporary",
        )

        self.MAX_DOCUMENT_SIZE = int(
            os.getenv(
                "MAX_DOCUMENT_SIZE",
                str(20 * 1024 * 1024),
            )
        )

        self.EMBEDDING_PROVIDER = os.getenv(
            "EMBEDDING_PROVIDER",
            "huggingface",
        )

        self.HF_TOKEN = os.getenv(
            "HF_TOKEN",
        )

        self.EMBEDDING_MODEL = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        self.EMBEDDING_DIMENSIONS = int(
            os.getenv(
                "EMBEDDING_DIMENSIONS",
                "384",
            )
        )
        self.RAG_TOP_K = int(
            os.getenv(
                "RAG_TOP_K",
                "3",
            )
        )

        self.RAG_MIN_SIMILARITY = float(
            os.getenv(
                "RAG_MIN_SIMILARITY",
                "0.20",
            )
        )

        self.RAG_MAX_CONTEXT_CHUNKS = int(
            os.getenv(
                "RAG_MAX_CONTEXT_CHUNKS",
                "5",
            )
        )

        self.CHAT_HISTORY_MESSAGE_LIMIT = int(
            os.getenv(
                "CHAT_HISTORY_MESSAGE_LIMIT",
                "8",
            )
        )

        self.CHAT_HISTORY_MAX_CHARACTERS = int(
            os.getenv(
                "CHAT_HISTORY_MAX_CHARACTERS",
                "12000",
            )
        )


settings = Settings()
