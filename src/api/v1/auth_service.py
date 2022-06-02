from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

import crud
from core import security
from core.config import app_settings
from db.models import Token, User
from exceptions import (
    InvalidLoginData,
    InvalidRefreshToken,
    NotFoundException,
    SomethingWentWrongException,
    UserIsBanned,
)
from schemas.token import TokenCreate, TokenUpdate


class AuthService:
    async def _login(self, db: AsyncSession, form_data: OAuth2PasswordRequestForm = Depends()) -> User:
        user = await crud.user.authenticate(db, email=form_data.username, password=form_data.password)
        if not user:
            raise InvalidLoginData()
        elif crud.user.is_banned(user):
            raise UserIsBanned()

        return user

    async def _create_tokens(self, db: AsyncSession, user: User) -> Token:
        access_token = security.create_access_token(
            user, expires_delta=timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = security.create_refresh_token(user)

        existing_token = await crud.token.get_by_email(db, email=user.email)
        if existing_token:
            return await self._update_tokens(db, existing_token, user)

        token_data: Token = await crud.token.create(
            db,
            obj_in=TokenCreate(email=user.email, access_token=access_token, refresh_token=refresh_token),
        )

        return token_data

    async def _update_tokens(self, db: AsyncSession, token: Token, user: User) -> Token:
        access_token = security.create_access_token(
            user, expires_delta=timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = security.create_refresh_token(user)

        token_data: Token = await crud.token.update(
            db,
            db_obj=token,
            obj_in=TokenUpdate(email=user.email, access_token=access_token, refresh_token=refresh_token),
        )

        return token_data

    async def login_and_create_tokens(
        self, db: AsyncSession, form_data: OAuth2PasswordRequestForm = Depends()
    ) -> Token:
        user = await self._login(db, form_data)

        token_data: Token = await self._create_tokens(db, user)

        return token_data

    async def refresh_tokens(self, db: AsyncSession, request: Request) -> Token:
        access_token: str = str(request.cookies.get("jwt-access"))
        refresh_token: str = str(request.cookies.get("jwt-refresh"))

        if not access_token and not refresh_token:
            raise InvalidRefreshToken()

        token_data = await crud.token.get_by_access_token(db, access_token=access_token)

        if not token_data:
            raise InvalidRefreshToken()

        if token_data.refresh_token != refresh_token:
            raise InvalidRefreshToken()

        user = await crud.user.get_by_email(db, email=token_data.email)

        if not user:
            raise NotFoundException()

        new_tokens = await self._update_tokens(db, token_data, user)

        return new_tokens

    async def _delete_tokens(self, db: AsyncSession, token: Token) -> str:
        removed_row = await crud.token.remove_by_email(db, email=token.email)
        if removed_row:
            return "Logout Successfully"

        raise SomethingWentWrongException()

    async def revoke_tokens(self, db: AsyncSession, request: Request) -> str:
        access_token: str = str(request.cookies.get("jwt-access"))
        refresh_token: str = str(request.cookies.get("jwt-refresh"))

        if not access_token and not refresh_token:
            return "Logout Successfully"

        token_data = await crud.token.get_by_access_token(db, access_token=access_token)

        if not token_data:
            return "Logout Successfully"

        if token_data.refresh_token != refresh_token:
            return "Logout Successfully"

        return await self._delete_tokens(db, token_data)
