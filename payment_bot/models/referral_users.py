import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.future import select

from .database import BaseModel, async_session
from .users_crm import UserCRM


class ReferralUsers(BaseModel):
    __tablename__ = 'referral_users'

    id_referral = Column(Integer, primary_key=True,
                         unique=True, autoincrement=True)
    api_referral = Column(String, default=uuid.uuid4().hex)
    count_referral = Column(Integer, default=0)
    count_subreferral = Column(Integer, default=0)

    # relationship out
    user_crm_id = Column(Integer, ForeignKey(
        'users_crm.id_user_crm'), nullable=False)
    user_crm = relationship(
        'UserCRM', backref='user_crm', cascade="all")

    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    async def referral_up(self):
        self.count_referral += 1
        await self.commit()

    @classmethod
    async def add_refer(cls, user_crm: UserCRM):

        refer = ReferralUsers(user_crm_id=user_crm.id_user_crm)
        cls = await refer.commit()
        return cls

    @classmethod
    async def from_api_referral(cls, api_referral: str):
        async with async_session() as session:
            result = await session.execute(
                select(ReferralUsers).where(
                    ReferralUsers.api_referral == api_referral)
            )
            userdb = result.scalars().first()
        cls = userdb
        return cls

    @classmethod
    async def from_user_crm(cls, user_crm: UserCRM):
        refer = ReferralUsers(user_crm_id=user_crm.id_user_crm)
        async with async_session() as session:
            result = await session.execute(
                select(ReferralUsers).where(
                    ReferralUsers.user_crm_id == refer.user_crm_id)
            )
            userdb = result.scalars().first()
        cls = userdb
        return cls
