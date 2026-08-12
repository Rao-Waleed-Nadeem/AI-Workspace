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


settings = Settings()