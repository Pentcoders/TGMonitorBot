from datetime import timedelta
import uuid
from sqlalchemy import Column, Integer, String, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.future import select

from .database import BaseModel, async_session


class Subscribtion(BaseModel):
    __tablename__ = 'subscriptions'

    id_subscriptions = Column(
        Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String, unique=True)
    price = Column(Integer)
    term = Column(Interval, default=timedelta(days=31))
    description = Column(String)
    count_card_monitoring = Column(Integer, default=1)
    count_channels_monitoring = Column(Integer, default=5)
    count_pattern_monitoring = Column(Integer, default=5)
    api_subscriptions = Column(String, default=uuid.uuid4().hex)


    @staticmethod
    async def get_count_subscribtion() -> int:
        count = 0
        async with async_session() as session:
            result = await session.execute(select(Subscribtion))
            count = len(result.scalars().all())
        return count

    @classmethod
    async def get_subscribtion_from_page(cls, page: int):

        async with async_session() as session:
            result = await session.execute(
                select(Subscribtion).order_by(Subscribtion.id_subscriptions.asc())
            )
            subscribtions = result.scalars().all()

        if len(subscribtions) < page:
            return None
        
        cls = subscribtions[page]
        return cls
    
    @classmethod
    async def get_subscribtion_from_api(cls, api: str):

        async with async_session() as session:
            result = await session.execute(
                select(Subscribtion).where(Subscribtion.api_subscriptions == api)
            )
            subscribtion = result.scalars().one()

        cls = subscribtion
        return cls

    @classmethod
    async def create_subscribtion(cls):

        test_sub = Subscribtion(
            title='Privat',
            price=100000,
            term=timedelta(days=93),
            description='Test Subscribtion Standart'
        )

        async with async_session() as session:
            session.add(test_sub)
            await session.commit()

        return test_sub
