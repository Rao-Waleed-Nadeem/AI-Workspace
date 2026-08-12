from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    return auth_service.register(
        db=db,
        request=request,
    )

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    # request: LoginRequest,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    request = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )
    return auth_service.login(
        db=db,
        request=request,
    )

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }