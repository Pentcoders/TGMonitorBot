from random import randint
import uuid

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.future import select

from .database import BaseModel, async_session
from .user_channels import UserChannels
from .users_crm import UserCRM


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

    async def set_channel_pushing(self, id_user_channel: int):
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
    async def create_card(user_crm:UserCRM):
        card = CardsMonitoring(title=f'Card id{randint(10000, 99999)}',
                               card_uuid=uuid.uuid4().hex,
                               description='Description not set',
                               user_crm_id=user_crm.id_user_crm,
                               is_running=True)

        return await card.commit()
    
   
