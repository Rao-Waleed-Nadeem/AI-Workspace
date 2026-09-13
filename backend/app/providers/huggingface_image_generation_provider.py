import base64
import time
from io import BytesIO
import logging

from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

from app.core.config import settings
from app.providers.base_image_generation_provider import (
    BaseImageGenerationProvider,
)
from app.providers.image_generation import GeneratedImage

logger = logging.getLogger(__name__)


class HuggingFaceImageGenerationProvider(
    BaseImageGenerationProvider
):

    def __init__(self):
        self.client = InferenceClient(
            api_key=settings.HF_TOKEN,
            timeout=120,
        )

    def generate_image(
        self,
        prompt: str,
    ) -> GeneratedImage:

        max_retries = settings.IMAGE_GENERATION_RETRIES
        base_delay = 5

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                image = self.client.text_to_image(
                    prompt=prompt,
                    model=settings.IMAGE_MODEL_NAME,
                )

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()
                encoded_image = base64.b64encode(image_bytes).decode("utf-8")

                return GeneratedImage(b64_json=encoded_image)

            except HfHubHTTPError as e:
                last_exception = e
                if attempt == max_retries:
                    break
                if e.response is not None and e.response.status_code in (429, 503, 524):
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        "Image generation attempt %d/%d failed (%s); retrying in %ds",
                        attempt + 1,
                        max_retries + 1,
                        e.response.status_code,
                        delay,
                    )
                    time.sleep(delay)
                    continue
                raise

            except Exception as e:
                last_exception = e
                if attempt == max_retries:
                    break
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "Image generation attempt %d/%d failed; retrying in %ds",
                    attempt + 1,
                    max_retries + 1,
                    delay,
                    exc_info=True,
                )
                time.sleep(delay)

        logger.error("Image generation failed after %d attempts", max_retries + 1)
        raise last_exception or RuntimeError("Image generation failed after retries")