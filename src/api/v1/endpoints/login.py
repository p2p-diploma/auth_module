from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from api.v1.auth_service import AuthService
from core import dependencies

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login(
    response: Response,
    db: AsyncSession = Depends(dependencies.async_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    token_data = await auth_service.login_and_create_tokens(db, form_data)

    response.set_cookie(key="jwt-access", value=token_data.access_token)
    response.set_cookie(key="jwt-refresh", value=token_data.access_token)

    return {
        "access_token": token_data.access_token,
        "refresh_token": token_data.refresh_token,
    }


@router.post("/refresh", response_model=schemas.Token)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(dependencies.async_session),
    auth_service: AuthService = Depends(),
) -> Any:
    """
    Refreshing access token
    """
    token_data = await auth_service.refresh_tokens(db, request)

    response.set_cookie(key="jwt-access", value=token_data.access_token)
    response.set_cookie(key="jwt-refresh", value=token_data.access_token)

    return {
        "access_token": token_data.access_token,
        "refresh_token": token_data.refresh_token,
    }


@router.post("/revoke")
async def revoke(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(dependencies.async_session),
    auth_service: AuthService = Depends(),
) -> str:
    """
    Refreshing access token
    """
    message: str = await auth_service.revoke_tokens(db, request)

    response.delete_cookie(key="jwt-access")
    response.delete_cookie(key="jwt-refresh")

    return message
