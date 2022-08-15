from xxlimited import Str
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from .cards_monitoring import CardsMonitoring
from .database import BaseModel, async_session


class PatternMonitoring(BaseModel):
    __tablename__ = 'patterns_monitoring'

    id_pattern = Column(
        Integer, primary_key=True, unique=True, autoincrement=True)
    pattern = Column(String)
    description = Column(String)
    # relationship out
    card_monitoring_id = Column(Integer, ForeignKey('cards_monitoring.id_card'), nullable=False)
    card_monitoring = relationship(
        'CardsMonitoring', backref=backref('pattern_monitoring', cascade="all, delete-orphan"), lazy='joined')

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
    
    async def change_pattern(self, pattern: Str):
        self.pattern = pattern
        await self.commit()
    
    async def change_description(self, description: Str):
        self.description = description
        await self.commit()
    
    @logger.catch(SQLAlchemyError)
    @staticmethod
    async def from_card(card: CardsMonitoring):
        async with async_session() as session:
            result = await session.execute(
                select(PatternMonitoring).\
                where(PatternMonitoring.card_monitoring_id == card.id_card))
            
            pattern_db: list[PatternMonitoring] = result.scalars().all()

        if pattern_db is None:
            return None

        return pattern_db
    
    @logger.catch(SQLAlchemyError)
    @staticmethod
    async def from_id_pattern(id_pattern: int):
        async with async_session() as session:
            result = await session.execute(
                select(PatternMonitoring).\
                where(PatternMonitoring.id_pattern == id_pattern))
            
            pattern_db: list[PatternMonitoring] = result.scalars().one_or_none()

        if pattern_db is None:
            return None

        return pattern_db
    
    @staticmethod
    async def add_pattern(card: CardsMonitoring, count_ptt: int,  pattern: str = None):
        ptt = PatternMonitoring(pattern=pattern,
                                description='undefined',
                               card_monitoring_id=card.id_card,
                               card_monitoring=card)

        async with async_session() as session:
            result = await session.execute(
                select(PatternMonitoring).
                where(PatternMonitoring.pattern == ptt.pattern,
                      PatternMonitoring.card_monitoring_id == ptt.card_monitoring_id)
            )
            ptt_db = result.scalars().first()

        if ptt_db is not None:
            return ptt_db

        async with async_session() as session:
            result = await session.execute(
                select(PatternMonitoring).
                where(PatternMonitoring.card_monitoring_id == ptt.card_monitoring_id)
            )
            all_ptt_db = result.scalars().all()
        if len(all_ptt_db) == count_ptt:
            return None
        return await ptt.commit()