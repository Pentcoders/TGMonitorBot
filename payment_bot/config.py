from loguru import logger
from envparse import env, ConfigurationError

try:
    DEBUG = env.str("DEBUG", default=True)
    
    
    # TOKEN Telegram bot
    TELEGRAM_TOKEN: str = env.str("TELEGRAM_TOKEN_PAYMENT_BOT", default="")
    TELEGRAM_TOKEN_SEND_BOT: str = env.str("TELEGRAM_TOKEN_SEND_BOT", default="")
    PAYMENT_TOKEN: str = env.str("PAYMENT_TOKEN", default="")
    # # webserver settings
    WEBHOOK_DOMAIN = env.str("WEBHOOK_DOMAIN", default="")
    WEBHOOK_PATH = ''
    WEBHOOK_URL = f"https://{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"
    
    PORT_EXPOSE_PAYMENT_BOT = env.str("PORT_EXPOSE_PAYMENT_BOT", default="")
    PAYMENT_HOST = "localhost"
    
    # DataBase settings
    POSTGRES_USER = env.str("POSTGRES_USER", default="")
    POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD", default="")
    POSTGRES_HOST = env.str("POSTGRES_HOST", default="")
    POSTGRES_PORT = env.str("POSTGRES_PORT", default="")
    POSTGRES_DB = env.str("POSTGRES_DB", default='crmbot_db')
    DATABASE_URL_DRIVER = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    # Redis default settings
    REDIS_HOST = env.str("REDIS_HOST", default="")
    REDIS_PORT = env.str("REDIS_PORT", default="")

    REDIS_FSM_STORAGE = 0
    REDIS_POOL_SIZE = 10

    LOGGER_FILE = 'logging/file_{time}.log'

    LOKI_HOST = env.str("LOKI_HOST", default="")
    LOKI_PORT = env.str("LOKI_PORT", default="")
    LOKI_URL = f"http://{LOKI_HOST}:{LOKI_PORT}/loki/api/v1/push"
    
    USERBOT_HOST = env.str("USERBOT_HOST", default="")
    USERBOT_PORT = env.str("PORT_EXPOSE_USER_BOT", default="")
    USERBOT_URL = f'http://{USERBOT_HOST}:{USERBOT_PORT}'
    
    # if DEBUG:
    #     from debug_config import *
    
    
except ConfigurationError as error:
    logger.error(f"[{error.__class__.__name__}] {error}")
    raise SystemExit(error)

