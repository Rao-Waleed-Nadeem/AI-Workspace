from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int
    attachment_type: str
    original_name: str
    mime_type: str
    storage_path: str
    size: int

    class Config:
        from_attributes = True