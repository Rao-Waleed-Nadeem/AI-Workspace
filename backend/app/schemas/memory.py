from datetime import datetime

from pydantic import BaseModel, Field


class MemoryCandidate(BaseModel):
    key: str = Field(
        min_length=1,
        max_length=100,
    )

    value: str = Field(
        min_length=1,
        max_length=1000,
    )


class MemoryExtractionResponse(BaseModel):
    memories: list[MemoryCandidate] = Field(
        default_factory=list,
    )


class MemoryResponse(BaseModel):
    id: int
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True