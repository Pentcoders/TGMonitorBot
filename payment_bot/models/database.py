from aiogram import Dispatcher
from loguru import logger
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL_DRIVER


Base = declarative_base()
async_session = sessionmaker(expire_on_commit=False,
                             class_=AsyncSession)


class BaseModel(Base):
    __abstract__ = True


@logger.catch
async def db_setup(dispatcher: Dispatcher):

    logger.info(f"[DB] Start connection database")
    engine = create_async_engine(DATABASE_URL_DRIVER)
    async with engine.begin() as conn:
        from models import (TGUsers,
                            Subscribtion,
                            UserCRM,
                            UserChannels,
                            PurchasedSubscriptions,
                            CardsMonitoring,
                            ChannelsMonitoring,
                            PatternMonitoring)

    async_session.configure(bind=engine)
    logger.info(f"[DB] Start connected database")
