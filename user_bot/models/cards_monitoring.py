import uuid
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.future import select

from .database import BaseModel, async_session
from .users_crm import UserCRM
from .user_channels import UserChannels
from .user_channels import UserChannels


class CardsMonitoring(BaseModel):
    __tablename__ = 'cards_monitoring'

    id_card = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    card_uuid = Column(String, default=uuid.uuid4().hex)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_running = Column(Boolean, default=False)
    # relationship out

    user_crm_id = Column(Integer, ForeignKey(
        'users_crm.id_user_crm'), nullable=False)
    user_crm: UserCRM = relationship(
        'UserCRM', backref=backref('card_monitoring', cascade="all, delete-orphan"), lazy='joined')
    
    channel_pushing_id = Column(Integer, ForeignKey(
        'user_channels.id_user_channel'), nullable=True, unique=True)
    channel_pushing: UserChannels = relationship(
        'UserChannels', backref=backref('channel_pushing'), lazy='joined')

    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    async def delete(self):
        async with async_session() as session:
            await session.delete(self)
            await session.commit()
        return self

    async def change_pushing_channels(self, id_user_channel: int):
        self.channel_pushing_id = id_user_channel
        await self.commit()

    async def change_title(self, title: str):
        self.title = title
        await self.commit()

    async def change_description(self, description: str):
        self.description = description
        await self.commit()

    async def update_status(self, status: bool):
        self.is_running = status
        await self.commit()
    
    @classmethod
    async def from_uuid(cls, card_uuid: str):
        async with async_session() as session:
            result = await session.execute(
                select(CardsMonitoring).where(
                    CardsMonitoring.card_uuid == card_uuid)
            )
            card_db = result.scalars().first()

        if card_db is None:
            return None

        cls = card_db
        return cls

    @staticmethod
    async def add_card(title: str,  channel: UserChannels, description: str = 'undefined'):
        card = CardsMonitoring(title=title,
                               description=description,
                               channel_pushing_id=channel.id_user_channel,
                               user_crm_id=channel.user_crm.id_user_crm,
                               channel_pushing=channel)

        async with async_session() as session:
            result = await session.execute(
                select(CardsMonitoring).
                where(CardsMonitoring.channel_pushing_id ==
                      card.channel_pushing_id)
            )
            card_db = result.scalars().first()

        if card_db is not None:
            return

        return await card.commit()

    staticmethod
    async def get_all_card(user_crm: UserCRM):
        async with async_session() as session:
            result = await session.execute(
                select(CardsMonitoring).
                join(UserChannels).
                join(UserCRM).
                where(CardsMonitoring.channel_pushing_id==UserChannels.id_user_channel,
                    UserChannels.user_crm_id == user_crm.id_user_crm)
            )
            return result.scalars().all()
