from typing import Optional

from pydantic import BaseModel, EmailStr

from db.models.user import UserRole


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_superuser: bool = False
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserForceCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole


class UserUpdate(UserBase):
    password: Optional[str] = None
    is_banned: Optional[bool] = False


class UserInDBBase(UserBase):
    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserProfile(BaseModel):
    email: EmailStr
    full_name: str

    class Config:
        orm_mode = True


class UserInDB(UserInDBBase):
    hashed_password: str
