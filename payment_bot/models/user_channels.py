from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.future import select

from .database import BaseModel, async_session
from .users_crm import UserCRM


class UserChannels(BaseModel):
    __tablename__ = 'user_channels'

    id_user_channel = Column(Integer, primary_key=True,
                             unique=True, autoincrement=True)

    id_channel_tg = Column(BigInteger)
    id_chat = Column(BigInteger)

    title_channel_tg = Column(String, nullable=True)
    is_creator = Column(Boolean, default=False)

    # relationship out
    user_crm_id = Column(Integer, ForeignKey(
        'users_crm.id_user_crm'), nullable=False)
    user_crm:UserCRM = relationship(
        'UserCRM', backref='user_channel', cascade="all", lazy='joined')

    def __eq__(self, other):
        if isinstance(other, UserChannels):
            return self.id_user_channel == other.id_user_channel
        return NotImplemented
    
    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    @classmethod
    async def from_id_channel(cls, id_channel:int):
        async with async_session() as session:
            result = await session.execute(
                select(UserChannels).where(
                    UserChannels.id_user_channel == id_channel)
            )
            channeldb = result.scalars().first()

        if channeldb is None:
            return None

        cls = channeldb
        return cls
    
    
    @classmethod
    async def from_dialog(cls, dialog: dict[str:str | int | bool], user_crm: UserCRM):
        async with async_session() as session:
            result = await session.execute(
                select(UserChannels).where(
                    UserChannels.id_channel_tg == dialog.get('id'),
                    UserChannels.user_crm_id == user_crm.id_user_crm)
            )
            channeldb = result.scalars().first()

        if channeldb is None:
            return None

        cls = channeldb
        return cls
