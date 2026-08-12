from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.schemas.document import (
    DocumentListResponse,
    DocumentMetadataResponse,
)

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.services.document_service import (
    process_document_upload,
    get_user_document,
    list_user_documents,
    process_document_upload,
    remove_user_document,
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

@router.get(
    "",
    response_model=DocumentListResponse,
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):

    documents = list_user_documents(
        db=db,
        user_id=current_user.id,
    )

    return {
        "documents": documents,
    }

@router.get(
    "/{document_id}",
    response_model=DocumentMetadataResponse,
)
def get_document_metadata(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):

    document = get_user_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    return document

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):

    remove_user_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

