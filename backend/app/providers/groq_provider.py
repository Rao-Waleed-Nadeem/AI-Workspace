from groq import Groq

from app.core.config import (
    GROQ_API_KEY,
    MODEL_NAME,
)

from app.providers.base_provider import (
    BaseAIProvider,
)


class GroqProvider(BaseAIProvider):

    def __init__(self):

        self.client = Groq(api_key=GROQ_API_KEY)

    def generate_response(
        self,
        message: str,
    ) -> str:

        completion = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        return completion.choices[0].message.content
