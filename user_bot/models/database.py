from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL_DRIVER, DATABASE_URL_DRIVER_ROOT, POSTGRES_DB
from sqlalchemy import inspect
from sqlalchemy import text


Base = declarative_base()
async_session = sessionmaker(expire_on_commit=False,
                             class_=AsyncSession)


class BaseModel(Base):
    __abstract__ = True


@logger.catch
async def db_startup():
    logger.info(f"[DataBase] Start connection database")
    engine_root = create_async_engine(DATABASE_URL_DRIVER_ROOT)     # Check if exists DataBase
    #first start  
    logger.info(f"[DataBase] Check if exists database {POSTGRES_DB}")
    async with engine_root.connect() as conn, conn.begin():
        db_if_exists = f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'"
        result = await conn.execute(text(db_if_exists))
        if_exists = result.one_or_none()
        if if_exists is None:
            logger.warning(f"[DataBase] Database not found {POSTGRES_DB}")
            await conn.execute(text("commit"))  
            await conn.execute(text(f"CREATE DATABASE {POSTGRES_DB} ENCODING 'utf8' TEMPLATE template1"))
            logger.warning(f"[DataBase] Database {POSTGRES_DB} created")
        else:
            logger.info(f"[DataBase] Database found {POSTGRES_DB}")
            
            
    from models import (
        TGUsers,
        Subscribtion,
        UserCRM,
        UserChannels,
        PurchasedSubscriptions,
        CardsMonitoring,
        ChannelsMonitoring,
        PatternMonitoring)
    
    __all_tables = (
        TGUsers,
        Subscribtion,
        UserCRM,
        UserChannels,
        PurchasedSubscriptions,
        CardsMonitoring,
        ChannelsMonitoring,
        PatternMonitoring)

    engine_db = create_async_engine(DATABASE_URL_DRIVER)            # Check if exists Tables
    async with engine_db.connect() as conn, conn.begin():
        tables = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names())
        logger.info(f"[DataBase] Verification of the necessary tables in base {POSTGRES_DB}")
        if any(table.__tablename__ not in tables 
           for table in __all_tables):
            logger.warning(f"[DataBase] Required tables not found in base {POSTGRES_DB}")
            await conn.run_sync(BaseModel.metadata.create_all)
            logger.warning(f"[DataBase] Required tables created in base {POSTGRES_DB}")
        else:
            logger.info(f"[DataBase] Required tables found in base {POSTGRES_DB}")
    async_session.configure(bind=engine_db)
    logger.info(f"DataBase connected")

