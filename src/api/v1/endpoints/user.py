from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from core import dependencies
from exceptions import NoPermissionToDo, NotFoundException, SameEmailError
from schemas import User, UserCreate
from schemas.user import UserForceCreate, UserProfile

router = APIRouter()


@router.post("/", response_model=User)
async def create_user(
    *,
    db: AsyncSession = Depends(dependencies.get_session),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise SameEmailError()

    user = await crud.user.create_user(db, obj_in=user_in)

    return user


@router.post("/force", response_model=User)
async def create_user_force(
    *,
    db: AsyncSession = Depends(dependencies.get_session),
    admin: dict[str, Any] = Depends(dependencies.current_admin),
    user_in: UserForceCreate,
) -> Any:
    """
    Force create of a new user.
    """
    if not user_in.role.is_child_of(admin["role"]):
        raise NoPermissionToDo()

    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise SameEmailError()

    user = await crud.user.create_user(db, obj_in=user_in)

    return user


@router.get("/", response_model=UserProfile)
async def get_user(
    *,
    db: AsyncSession = Depends(dependencies.get_session),
    current_user: dict[str, Any] = Depends(dependencies.get_current_user_data),
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=current_user["user_id"])
    if user:
        return user

    raise NotFoundException()
