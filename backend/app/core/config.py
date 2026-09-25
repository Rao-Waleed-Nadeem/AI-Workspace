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

        self.IMAGE_MODEL_NAME = os.getenv(
            "IMAGE_MODEL_NAME",
            "black-forest-labs/FLUX.1-schnell",
        )

        self.IMAGE_GENERATION_RETRIES = int(
            os.getenv(
                "IMAGE_GENERATION_RETRIES",
                "1",
            )
        )

        self.HF_TOKEN = os.getenv(
            "HF_TOKEN",
        )

        self.EMBEDDING_MODEL = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        self.GENERATED_IMAGE_DIR = os.getenv(
            "GENERATED_IMAGE_DIR",
            "uploads/generated_images",
        )

        self.GENERATED_IMAGE_EXPIRATION_HOURS = int(
            os.getenv(
                "GENERATED_IMAGE_EXPIRATION_HOURS",
                "24",
            )
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

        self.MEMORY_MAX_ITEMS = int(
            os.getenv(
                "MEMORY_MAX_ITEMS",
                "20",
            )
        )

        self.SPEECH_TO_TEXT_MODEL_NAME = os.getenv(
            "SPEECH_TO_TEXT_MODEL_NAME",
            "whisper-large-v3-turbo",
        )

        self.MAX_AUDIO_SIZE = int(
            os.getenv(
                "MAX_AUDIO_SIZE",
                str(25 * 1024 * 1024),
            )
        )

        self.TEXT_TO_SPEECH_MODEL_NAME = os.getenv(
            "TEXT_TO_SPEECH_MODEL_NAME",
            "",
        ).strip()

        self.TEXT_TO_SPEECH_VOICE = os.getenv(
            "TEXT_TO_SPEECH_VOICE",
            "",
        ).strip()

        self.TEXT_TO_SPEECH_CHUNK_SIZE = int(
            os.getenv(
                "TEXT_TO_SPEECH_CHUNK_SIZE",
                "200",
            )
        )

        self.MAX_TEXT_TO_SPEECH_CHARACTERS = int(
            os.getenv(
                "MAX_TEXT_TO_SPEECH_CHARACTERS",
                "2000",
            )
        )

        self.LOG_LEVEL = os.getenv(
            "LOG_LEVEL",
            "INFO",
        )

        self.AI_RATE_LIMIT_REQUESTS = int(
            os.getenv(
                "AI_RATE_LIMIT_REQUESTS",
                "20",
            )
        )

        self.AI_RATE_LIMIT_WINDOW_SECONDS = int(
            os.getenv(
                "AI_RATE_LIMIT_WINDOW_SECONDS",
                "60",
            )
        )

        self.AUTH_RATE_LIMIT_REQUESTS = int(
            os.getenv(
                "AUTH_RATE_LIMIT_REQUESTS",
                "10",
            )
        )

        self.AUTH_RATE_LIMIT_WINDOW_SECONDS = int(
            os.getenv(
                "AUTH_RATE_LIMIT_WINDOW_SECONDS",
                "60",
            )
        )

        self.AI_CONTEXT_WINDOW_TOKENS = int(
            os.getenv(
                "AI_CONTEXT_WINDOW_TOKENS",
                "8192",
            )
        )

        self.AI_MAX_INPUT_TOKENS = int(
            os.getenv(
                "AI_MAX_INPUT_TOKENS",
                "6000",
            )
        )

        self.AI_MAX_OUTPUT_TOKENS = int(
            os.getenv(
                "AI_MAX_OUTPUT_TOKENS",
                "1200",
            )
        )

        self.TOKEN_ESTIMATE_CHARS_PER_TOKEN = float(
            os.getenv(
                "TOKEN_ESTIMATE_CHARS_PER_TOKEN",
                "4",
            )
        )

        self.AI_MAX_TOOL_CALLS = int(
            os.getenv(
                "AI_MAX_TOOL_CALLS",
                "3",
            )
        )

    @staticmethod
    def _required_env(name: str) -> str:
        value = os.getenv(name, "").strip()

        if not value:
            raise RuntimeError(f"Required environment variable is missing: {name}")

        return value


settings = Settings()
