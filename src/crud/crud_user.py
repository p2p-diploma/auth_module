from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from db.models.user import User, UserRole
from schemas.user import UserCreate, UserForceCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_admin(self, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).filter(User.role == UserRole.SUPERUSER))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, *, obj_in: Union[UserCreate, UserForceCreate]) -> User:
        is_superuser: bool = False
        try:
            role: UserRole = obj_in.role
            if obj_in.role == UserRole.SUPERUSER:
                is_superuser = True
        except AttributeError:
            role = UserRole.USER

        db_obj = User(
            role=role,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        password = update_data.pop("password", None)
        if password:
            hashed_password = get_password_hash(password)
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_banned(self, user: User) -> bool:
        return user.is_banned

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
