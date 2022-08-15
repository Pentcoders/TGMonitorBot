from aiogram import types
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from .database import BaseModel, async_session


class UserAdmin(BaseModel):
    __tablename__ = 'users_admin'

    id_user_admin = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    id_user_tg = Column(Integer, unique=True)
    user_name = Column(String)

    @classmethod
    async def from_user(cls, user: types.User):

        tg_user = UserAdmin(id_user_tg=user.id,
                          user_name=user.username,
                          full_name=user.full_name)

        async with async_session() as session:
            result = await session.execute(
                select(UserAdmin).where(UserAdmin.id_user_tg == tg_user.id_user_tg)
            )
            userdb = result.scalars().first()

        cls = await tg_user.commit() if not userdb else userdb
        return cls

    @classmethod
    async def from_message(cls, messge: types.Message):
        return await UserAdmin.from_user(messge.from_user)
