import uuid

from aiogram import types
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import PhoneNumberType
from sqlalchemy.orm import relationship
from sqlalchemy.future import select

from .database import BaseModel, async_session
from .tg_users import TGUsers


class UserCRM(BaseModel):
    __tablename__ = 'users_crm'

    id_user_crm = Column(Integer, primary_key=True,
                         unique=True, autoincrement=True)
    uuid_user = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    phone_number = Column(PhoneNumberType(region='RU'), nullable=True, default=None)
    password = Column(String, nullable=True, default=None)
    is_authorized = Column(Boolean, default=False)
    
    # relationship out
    tg_user_id = Column(Integer, ForeignKey(
        'tg_users.id_user'), nullable=False)
    tg_user = relationship("TGUsers", backref="user_crm", lazy='joined')


    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    async def set_phone_number(self, contact: types.Contact):
        if isinstance(contact, str):
            self.phone_number = contact
        if isinstance(contact, types.Contact):
            self.phone_number = contact.phone_number
        await self.commit()

    async def set_password(self, password: str):
        if isinstance(password, str):
            self.password = password
            await self.commit()
            return True
        return False
    
    async def set_authorized(self, authorized: bool):
        if isinstance(authorized, bool):
            self.is_authorized = authorized
            await self.commit()
            return True
        return False

    @classmethod
    async def from_uuid_user(cls, uuid_user: str):

        async with async_session() as session:
            result = await session.execute(
                select(UserCRM).where(UserCRM.uuid_user == uuid_user)
            )
            userdb = result.scalars().first()

        cls = userdb
        return cls

    @classmethod
    async def from_tg_user(cls, tg_user: TGUsers):

        async with async_session() as session:
            result = await session.execute(
                select(UserCRM).where(UserCRM.tg_user_id == tg_user.id_user)
            )
            userdb = result.scalars().first()

        cls = userdb
        return cls

    @classmethod
    async def add_user_crm(cls, tg_user: TGUsers):

        user_crm = UserCRM(tg_user_id=tg_user.id_user, 
                           tg_user=tg_user)

        async with async_session() as session:
            result = await session.execute(
                select(UserCRM).where(
                    UserCRM.tg_user_id == user_crm.tg_user_id)
            )
            userdb = result.scalars().first()

        cls = await user_crm.commit() if not userdb else userdb
        
        return cls

    @staticmethod
    async def all_user_is_authorized():
        async with async_session() as session:
            result = await session.execute(
                select(UserCRM).where(UserCRM.is_authorized == True)
            )
            return result.scalars().all()
        
    