import base64

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_current_user,
)

from app.models.user import User

from app.schemas.text_to_speech import (
    TextToSpeechRequest,
    TextToSpeechResponse,
)

from app.services.text_to_speech_service import (
    TextToSpeechService,
)


router = APIRouter(
    prefix="/speech",
    tags=["Speech"],
)


@router.post(
    "/synthesize",
    response_model=TextToSpeechResponse,
)
def synthesize_speech(
    request: TextToSpeechRequest,
    current_user: User = Depends(
        get_current_user
    ),
):

    service = TextToSpeechService()

    audio_chunks = service.synthesize(
        request.text
    )

    return TextToSpeechResponse(
        audio_chunks=[
            base64.b64encode(
                chunk
            ).decode("ascii")
            for chunk in audio_chunks
        ]
    )