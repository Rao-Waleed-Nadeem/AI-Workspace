from pydantic import BaseModel


class StructuredResponse(BaseModel):
    title: str
    summary: str
    keywords: list[str]
