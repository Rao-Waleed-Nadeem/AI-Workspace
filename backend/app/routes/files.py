from fastapi import APIRouter, Depends, File, UploadFile

from app.core.dependencies import get_current_user
from app.models import User
from app.services.file_upload_service import save_temporary_upload


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    uploaded_file = await save_temporary_upload(
        file,
    )

    return {
        "message": "File uploaded successfully.",
        "file": uploaded_file,
    }