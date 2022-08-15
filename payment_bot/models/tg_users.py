from aiogram import types
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.future import select

from .database import BaseModel, async_session


class TGUsers(BaseModel):
    __tablename__ = 'tg_users'

    id_user = Column(Integer, primary_key=True,
                     unique=True, autoincrement=True)
    id_user_tg = Column(BigInteger, unique=True)
    user_name = Column(String)
    full_name = Column(String)
    api_refer = Column(String)
    # relationship
    # user_crm = relationship('UserCRM', back_populates='tg_user')

    async def set_api_refer(self, api_refer: str):
        if (api_refer.isalnum()
            and len(api_refer) == 32
                and self.api_refer == None):
            self.api_refer = api_refer
            await self.commit()

    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    @classmethod
    async def from_user(cls, user: types.User):

        tg_user = TGUsers(id_user_tg=user.id,
                          user_name=user.username,
                          full_name=user.full_name)

        async with async_session() as session:
            result = await session.execute(
                select(TGUsers).where(TGUsers.id_user_tg == tg_user.id_user_tg)
            )
            userdb = result.scalars().first()

        cls = await tg_user.commit() if not userdb else userdb
        return cls

    @classmethod
    async def from_message(cls, message: types.Message):
        user = message.from_user
        if user.is_bot:
            user = message.chat
        return await TGUsers.from_user(user)
