from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from .database import BaseModel, async_session
from .cards_monitoring import CardsMonitoring
from .user_channels import UserChannels
from .purchased_subscriptions import PurchasedSubscriptions


class ChannelsMonitoring(BaseModel):
    __tablename__ = 'channels_monitoring'

    id_monitoring = Column(
        Integer, primary_key=True, unique=True, autoincrement=True)

    # relationship out
    channel_monitoring_id = Column(Integer, ForeignKey(
        'user_channels.id_user_channel'), nullable=False)
    channel_monitoring:UserChannels = relationship(
        'UserChannels', backref='channel_monitoring', lazy='joined')

    card_monitoring_id = Column(Integer, ForeignKey(
        'cards_monitoring.id_card'), nullable=False)
    card_monitoring = relationship(
        'CardsMonitoring', backref=backref('card_monitoring', cascade="all, delete-orphan"),  lazy='joined')

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

    @logger.catch(SQLAlchemyError)
    @staticmethod
    async def from_card(card: CardsMonitoring):
        async with async_session() as session:
            result = await session.execute(
                select(ChannelsMonitoring).\
                where(ChannelsMonitoring.card_monitoring_id == card.id_card))
            
            channels_db: list[ChannelsMonitoring] = result.scalars().all()

        if channels_db is None:
            return None

        return channels_db

    @logger.catch(SQLAlchemyError)
    @staticmethod
    async def add_or_pop_channel(card: CardsMonitoring, channel: UserChannels):
        ch_monitoring = ChannelsMonitoring(
            card_monitoring_id=card.id_card,
            channel_monitoring_id=channel.id_user_channel,)
        
        async with async_session() as session:
            result = await session.execute(
                select(ChannelsMonitoring).\
                where(ChannelsMonitoring.card_monitoring_id == ch_monitoring.card_monitoring_id,
                      ))
            
            channel_db:list[ChannelsMonitoring] = result.scalars().all()

        if len(channel_db) == 0:
            return await ch_monitoring.commit()
        
        for ch_db in channel_db:
            if ch_monitoring.channel_monitoring_id == ch_db.channel_monitoring_id:
                await ch_db.delete()
                return 'ChannelDelete'
        
        id_user_crm = card.channel_pushing.user_crm.id_user_crm
        pursh_sub = await PurchasedSubscriptions.from_user_crm_id(id_user_crm)
        count_channel = pursh_sub.subscribtion.count_channels_monitoring
        
        if count_channel <= len(channel_db):
            return 'StorageIsTaken'
        
        return await ch_monitoring.commit()