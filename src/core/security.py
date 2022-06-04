from datetime import datetime, timedelta
from typing import Any, Optional

import jwt as py_jwt
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from starlette import status
from starlette.requests import Request

from core.config import app_settings
from db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> Any:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_body = {"user_id": user.email, "role": user.role.value, "exp": expire}
    encoded_jwt = jwt.encode(access_body, app_settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user: User, expires_delta: Optional[timedelta] = None) -> Any:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=app_settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_body = {
        "email": user.email,
        "created_at": user.created_at.strftime("MM:SS"),
        "exp": expire,
    }
    encoded_jwt = jwt.encode(access_body, app_settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def encode_access_token(request: Request) -> Any:
    unauthorized_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    raw_jwt = request.cookies.get("jwt-access")

    if raw_jwt is None:
        raise unauthorized_exc
    try:
        payload = jwt.decode(
            raw_jwt,
            app_settings.SECRET_KEY,
            algorithms=["HS256"],
        )
    except py_jwt.PyJWTError as e:
        raise unauthorized_exc from e

    return payload


def verify_password(plain_password: str, hashed_password: str) -> Any:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> Any:
    return pwd_context.hash(password)
