from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import jwt

from app.core.config import settings
from app.database import get_db
from app.models import User
from app.repositories.user_repository import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        jwt.InvalidTokenError,
        ValueError,
    ):
        raise credentials_exception

    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise credentials_exception

    return user