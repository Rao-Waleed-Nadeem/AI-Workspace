from datetime import datetime

from pydantic import BaseModel


class DocumentMetadataResponse(BaseModel):
    id: int
    original_name: str
    mime_type: str
    size: int
    page_count: int
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadataResponse]