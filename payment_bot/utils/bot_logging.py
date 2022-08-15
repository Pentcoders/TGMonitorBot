import functools
import logging
from typing import ParamSpec, TypeVar, Callable

from aiogram import types, exceptions, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.storage import FSMContext
import logging_loki
from loguru import logger
from config import LOGGER_FILE, LOKI_URL, DEBUG

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

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def intercept_logging():
    # logging.basicConfig(level=logging.INFO)
    loggers: list[logging.Logger] = []
    for name in logging.root.manager.loggerDict:
        if name.startswith("gunicorn.") or name.startswith("aiogram."):
            loggers.append(logging.getLogger(name))
        else:
            logging.getLogger(name).handlers = [InterceptHandler()]
    for gunicorn_logger in loggers:
        gunicorn_logger.handlers = []
    logging.getLogger("gunicorn").handlers = [InterceptHandler()]
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("aiogram").handlers = [InterceptHandler()]

        
async def logging_setup(dispatcher: Dispatcher):
    handler = logging_loki.LokiHandler(
        url=LOKI_URL,
        tags={"application": "payment_bot"},
        version="1",
    )
    logger.add(LOGGER_FILE, level="INFO", rotation="5 MB",
               enqueue=True, backtrace=True, diagnose=True)
    logger.add(handler,level="INFO",
               enqueue=True, backtrace=True, diagnose=True)
    logger.info(f"Setup loguru")
    logger.info("Setup logging middleware.")
    middleware_logger = LoggingMiddleware()
    middleware_logger.logger = logger
    dispatcher.middleware.setup(middleware_logger)


def log_handler(func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Callable[P, T]:
        result: str = ''
        state: FSMContext = kwargs.get('state')
        user: str = f"User @{args[0].from_user.username} [id{args[0].from_user.id}]"

        if isinstance(args[0], types.Message):
            result = args[0].text
        if isinstance(args[0], types.CallbackQuery):
            result = args[0].data

        try:
            logger.info(
                f"{user} event function [{func.__name__}] Entered value: {result}")
            return await func(*args, **kwargs)

        except exceptions.BotBlocked as error:
            logger.error(f"[{error.__class__.__name__} -> {error}] {user}")
            await state.finish()

        except Exception as error:
            if DEBUG:
                logger.exception(
                    f"[{error.__class__.__name__} -> {error}] {user} event function [{func.__name__}].")
            logger.error(
                f"[{error.__class__.__name__} -> {error}] {user} event function [{func.__name__}].")

    return logger.catch(wrapper)


def log_payment(func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Callable[P, T]:

        if isinstance(args[0], types.Message):
            message = args[0]
        if isinstance(args[0], types.CallbackQuery):
            message = args[0].message

        user: str = f"User @{message.from_user.username} [id{message.from_user.id}]"
        subscription = message.successful_payment.invoice_payload
        total_amount = message.successful_payment.total_amount / 100
        currency = message.successful_payment.currency
        try:
            logger.info(
                f"{user} paid: [{subscription}] Entered {total_amount} {currency}")
            return await func(*args, **kwargs)

        except exceptions.BotBlocked as error:
            logger.error(f"[{error.__class__.__name__} -> {error}] {user}")
            state: FSMContext = kwargs.get('state')
            await state.finish()

        except Exception as error:
            if DEBUG:
                logger.exception(
                    f"[{error.__class__.__name__} -> {error}] {user} event function [{func.__name__}].")
            logger.error(
                f"[{error.__class__.__name__} -> {error}] {user} event function [{func.__name__}].")

    return logger.catch(wrapper)


