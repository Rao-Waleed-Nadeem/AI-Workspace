from fastapi import APIRouter, Depends, File, UploadFile

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.speech import SpeechToTextResponse
from app.services.speech_to_text_service import SpeechToTextService


router = APIRouter(
    prefix="/speech",
    tags=["Speech"],
)


@router.post(
    "/transcribe",
    response_model=SpeechToTextResponse,
)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    service = SpeechToTextService()

    transcript = await service.transcribe(file)

    return SpeechToTextResponse(
        transcript=transcript,
    )