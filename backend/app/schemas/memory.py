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