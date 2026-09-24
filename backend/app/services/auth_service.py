from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.security import (hash_password, verify_password, create_access_token)
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
)
from app.schemas.auth import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
    TokenResponse,
)


class AuthService:

    def register(
        self,
        db: Session,
        request: RegisterRequest,
    ) -> UserResponse:

        existing_user = get_user_by_email(
            db=db,
            email=request.email,
        )

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

        password_hash = hash_password(
            request.password,
        )

        user = create_user(
            db=db,
            email=request.email,
            password_hash=password_hash,
        )

        db.commit()

        return UserResponse(
            id=user.id,
            email=user.email,
        )

    def login(
        self,
        db: Session,
        request: LoginRequest,
    ) -> TokenResponse:

        user = get_user_by_email(
            db=db,
            email=request.email,
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        access_token = create_access_token(
            user_id=user.id,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )
