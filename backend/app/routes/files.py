from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.services.document_service import (
    process_document_upload,
)


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):

    document = await process_document_upload(
        db=db,
        file=file,
        user_id=current_user.id,
    )

    return {
        "message": "Document uploaded and processed successfully.",
        "document": {
            "id": document.id,
            "original_name": document.original_name,
            "mime_type": document.mime_type,
            "size": document.size,
            "page_count": document.page_count,
            "created_at": document.created_at,
        },
    }