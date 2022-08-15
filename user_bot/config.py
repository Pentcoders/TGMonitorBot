

from loguru import logger

from envparse import env, ConfigurationError


try:
    DEBUG = env.str("DEBUG", default=True)
    
    # TOKEN Telegram bot
    API_ID = env.str("API_ID", default="")
    API_HASH = env.str("API_HASH", default="")
    TELEGRAM_TOKEN_SEND_BOT: str = env.str("TELEGRAM_TOKEN_SEND_BOT", default="")
    # DataBase settings
    POSTGRES_USER = env.str("POSTGRES_USER", default="")
    POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD", default="")
    POSTGRES_HOST = env.str("POSTGRES_HOST", default="")
    POSTGRES_DB = env.str("POSTGRES_DB", default='crmbot_db')
    DATABASE_URL_DRIVER_ROOT = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432"
    DATABASE_URL_DRIVER = f"{DATABASE_URL_DRIVER_ROOT}/{POSTGRES_DB}"
    # Redis default settings
    REDIS_HOST = env.str("REDIS_HOST", default="")
    REDIS_PORT = env.str("REDIS_PORT", default="")
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    
    NUMBER_STORAGE_SESSION = 3

    LOGGER_FILE = 'logging/file_{time}.log'

    LOKI_HOST = env.str("LOKI_HOST", default="")
    LOKI_PORT = env.str("LOKI_PORT", default="")
    LOKI_URL = f"http://{LOKI_HOST}:{LOKI_PORT}/loki/api/v1/push"
    
    NAME_SIGNAL_BOT = env.str("NAME_SIGNAL_BOT", default="crm_testads_bot")
    
    # if DEBUG:
    #     from debug_config import *
    
except ConfigurationError as error:
    logger.error(f"[{error.__class__.__name__}] {error}")
    raise SystemExit(error)

