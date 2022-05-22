from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenCreate(BaseModel):
    email: EmailStr
    access_token: str
    refresh_token: str


class TokenUpdate(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
