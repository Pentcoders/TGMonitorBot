import asyncio
import aiogram
import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.executor import Executor
from aiogram.dispatcher.webhook import WebhookRequestHandler
from loguru import logger

import config
from models.database import db_setup
from models import PurchasedSubscriptions
from utils import logging_setup, intercept_logging


try:
    fsm_storage = RedisStorage2(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_FSM_STORAGE,
        pool_size=config.REDIS_POOL_SIZE,
        prefix='FSM_REDIS_STORAGE'
    )

    bot = Bot(config.TELEGRAM_TOKEN)
    dp = Dispatcher(bot, storage=fsm_storage)
    execut = Executor(dp, skip_updates=True)
    PURCHASED_SUBSCRIPTIONS: dict[int, PurchasedSubscriptions] = {}

except (aiogram.exceptions.BadRequest, RuntimeError) as error:
    logger.exception(f"[{error.__class__.__name__}] {error}")
    raise SystemExit(f"[{error.__class__.__name__} -> {__name__}] {error}")


async def run_pending():
    logger.info("Run sheduling")
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(0.1)


async def start_aioschedule(dispatcher: Dispatcher):
    from botrequests.payment_menu import check_purchased_subscription
    
    all_purch = await PurchasedSubscriptions.get_all_purchased_subscription()
    PURCHASED_SUBSCRIPTIONS.update(all_purch)
    aioschedule.every().days.at("10:00").do(check_purchased_subscription)
    asyncio.create_task(run_pending())   
    
    
async def start_bot(dispatcher: Dispatcher):
    logger.info("Import handlers payment_bot")
    import botrequests
    import utils.bot_state
    logger.info("Setup Executor aiogram: {url}", url=config.WEBHOOK_URL)
    await dispatcher.bot.set_webhook(config.WEBHOOK_URL)


async def start_bot_polling(dispatcher: Dispatcher):
    logger.info("Import handlers payment_bot")
    import botrequests
    import utils.bot_state


async def shutdown(dispatcher: Dispatcher):
    logger.warning('Shutting down..')
    await dispatcher.bot.delete_webhook()


@logger.catch
def run_debug():
    intercept_logging()
    try:
        logger.info("Setup basic settings")
        execut.on_startup([logging_setup, db_setup, start_bot, start_aioschedule],
                          webhook=True, polling=False)
        execut.on_shutdown(shutdown)
        execut.start_webhook(webhook_path=config.WEBHOOK_PATH,
                             host=config.PAYMENT_HOST,
                             port=config.PORT_EXPOSE_PAYMENT_BOT)
    except SystemExit as error:
        logger.exception(error)
        
@logger.catch
def run_polling():
    intercept_logging()
    try:
        logger.info("Setup basic settings")
        execut.on_startup([logging_setup, db_setup, start_bot_polling, start_aioschedule],
                          webhook=False, polling=True)
        execut.on_shutdown(shutdown)
        execut.start_polling()
    except SystemExit as error:
        logger.exception(error)


@logger.catch
async def run_bot():
    intercept_logging()
    try:
        logger.info("Setup basic settings")
        execut.on_startup([logging_setup, db_setup, start_bot],
                          webhook=True, polling=False)
        execut.on_shutdown(shutdown)
        execut._prepare_webhook(
            path=config.WEBHOOK_PATH, handler=WebhookRequestHandler, route_name='webhook_handler')
        return execut.web_app
    except SystemExit as error:
        logger.exception(error)
