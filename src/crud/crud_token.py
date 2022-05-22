from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from db.models.user import Token
from schemas.token import TokenCreate, TokenUpdate


class CRUDToken(CRUDBase[Token, TokenCreate, TokenUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Token]:
        result = await db.execute(select(Token).filter(Token.email == email))
        return result.scalars().first()

    async def get_by_access_token(self, db: AsyncSession, *, access_token: str) -> Optional[Token]:
        result = await db.execute(select(Token).filter(Token.access_token == access_token))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: TokenCreate) -> Token:
        db_obj = Token(
            email=obj_in.email,
            access_token=obj_in.access_token,
            refresh_token=obj_in.refresh_token,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Token, obj_in: Union[TokenUpdate, Dict[str, Any]]
    ) -> Token:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def remove_by_email(self, db: AsyncSession, *, email: str) -> Optional[Token]:
        obj = await self.get_by_email(db, email=email)
        await db.delete(obj)
        await db.commit()
        return obj


token = CRUDToken(Token)
