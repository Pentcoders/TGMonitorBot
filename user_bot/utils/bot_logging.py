import logging
import functools
import time
from typing import ParamSpec, TypeVar, Callable


import logging_loki
from loguru import logger
from config import DEBUG, LOGGER_FILE, LOKI_URL
from telethon.errors import SessionPasswordNeededError, FloodWaitError, PhoneCodeExpiredError, UserBotError

# Type hinting
P = ParamSpec('P')
T = TypeVar('T')




class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage())


def intercept_logging():
    loggers: list[logging.Logger] = []
    for name in logging.root.manager.loggerDict:
        if name.startswith("uvicorn."):
            loggers.append(logging.getLogger(name))
        else:
            # logger.info(f'[UPDATE] Logging handler {name}')
            logging.getLogger(name).handlers = [InterceptHandler()]
    for gunicorn_logger in loggers:
        gunicorn_logger.handlers = []
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger('telethon').setLevel(level=logging.INFO)


async def logging_startup():
    handler = logging_loki.LokiHandler(
        url=LOKI_URL,
        tags={"application": "user_bots"},
        version="1"
    )
    logger.add(LOGGER_FILE, level="INFO", rotation="5 MB",
               enqueue=True, backtrace=True, diagnose=True)
    logger.add(handler, level="INFO", enqueue=True,
               backtrace=True, diagnose=True)

    logger.info(f"Setup loguru")


class tele_log:
    def __init__(self, message_log: str = ''):
        self._message_log: str = message_log

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Callable[P, T]:
            try:
                obj = args[0]
                logger.info(f'[TGUB/{func.__name__}] {obj} -> {self._message_log}')
                return await func(*args, **kwargs)

            except FloodWaitError as error:
                logger.error(
                    f'[TGUB/{func.__name__}] Flood waited for {time.strftime("%H:%M:%S", time.gmtime(error.seconds)) } seconds', error)

            except OSError as error:
                logger.error(
                    f"[TGUB/{func.__name__}] {error.__class__.__name__} -> {error}.")
            
            except AttributeError as error:
                logger.error(f"[TGUB/{func.__name__}] {error}.")

            except Exception as error:
                if DEBUG:
                    logger.exception(
                        f"[TGUB/{func.__name__}] {error.__class__.__name__} -> {error}.")
                logger.error(
                    f"[TGUB/{func.__name__}] {error.__class__.__name__} -> {error}.")

        return wrapper
