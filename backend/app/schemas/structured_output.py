from pydantic import BaseModel


class StructuredAIResponse(BaseModel):
    title: str
    summary: str
    keywords: list[str]


class StructuredResponse(BaseModel):
    chat_id: int
    title: str
    summary: str
    keywords: list[str]
