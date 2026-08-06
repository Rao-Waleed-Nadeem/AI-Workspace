from groq import Groq

from app.core.config import settings

from app.providers.base_provider import (
    BaseAIProvider,
)
# from backend.app import tools


class GroqProvider(BaseAIProvider):

    def __init__(self):

        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_response(
        self,
        messages: list[dict],
    ) -> str:

        completion = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Always format your responses using Markdown. "
                        "Use headings when appropriate, bullet or numbered lists "
                        "for lists, bold or italic text when useful, and fenced "
                        "code blocks with the correct language identifier for code."
                    ),
                },
                *messages,
            ],
        )

        return completion.choices[0].message.content

    def stream_response(
        self,
        messages: list[dict],
    ):

        stream = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Always format your responses using Markdown. "
                        "Use headings when appropriate, bullet or numbered lists "
                        "for lists, bold or italic text when useful, and fenced "
                        "code blocks with the correct language identifier for code."
                    ),
                },
                *messages,
            ],
            stream=True,
        )

        for chunk in stream:

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta

    def generate_structured_response(
        self,
        messages: list[dict],
    ) -> str:

        completion = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            response_format={
                "type": "json_object",
            },
        )

        return completion.choices[0].message.content

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):

        completion = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = completion.choices[0].message

        print("CONTENT:", message.content)
        print("TOOL CALLS:", message.tool_calls)

        return message

    def generate_vision_response(
        self,
        messages: list[dict],
    ) -> str:

        completion = self.client.chat.completions.create(
            model=settings.VISION_MODEL_NAME,
            messages=messages,
        )

        return completion.choices[0].message.content