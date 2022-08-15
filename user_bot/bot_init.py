import asyncio

from fastapi import FastAPI

from utils.bot_logging import *
from bot_core import TGclientChannelMonitoring
from models import db_startup, UserCRM, CardsMonitoring
from utils import logging_startup, intercept_logging


ALL_SESSION: dict[str, TGclientChannelMonitoring] = {}

# intercept uvicorn logging
intercept_logging()

app = FastAPI(
    title=__name__,
    root_path="/")

async def startup_bots():
    for user_crm in await UserCRM.all_user_is_authorized():
        if user_crm is None:
            continue
        if (user_crm.phone_number is None):
            continue
        user_bot = TGclientChannelMonitoring(
            user_name=user_crm.tg_user.user_name,
            phone_number=user_crm.phone_number.e164,
            uuid_user=str(user_crm.uuid_user))

        all_card:list[CardsMonitoring] = await CardsMonitoring.get_all_card(user_crm)
        
        for card in all_card:
            await card.update_status(False)
            
        if await user_bot.is_authorized():
            ALL_SESSION[str(user_crm.uuid_user)] = user_bot
            await user_bot.get_all_user_channels()
            await user_bot.start_monitoring()
            
             
            
@app.get('/health_check_app')
async def health_check_app():
    return 'health_check_app'

@app.on_event("startup")
async def startup():
    await logging_startup()
    await db_startup()
    import routes
    await startup_bots()


@app.on_event("shutdown")
async def shutdown():
    pass
