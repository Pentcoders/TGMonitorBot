import asyncio
from loguru import logger

from models import UserCRM
from bot_core import TGclientChannelMonitoring
from bot_init import app, ALL_SESSION
from ..schema import UserAuthorized


@app.get('/created_userbot/{user_uuid}')
async def created_userbot_endpoint(user_uuid: str):
    logger.info(f'[GET] Start EndPoint created_userbot. Params: [{user_uuid}]')
    user_crm: UserCRM = await UserCRM.from_uuid_user(user_uuid)
    user_bot = ALL_SESSION.get(user_uuid)
    phone_number = user_crm.phone_number.e164
    if user_bot is None and user_crm is not None:
        user_bot = TGclientChannelMonitoring(
            user_name=user_crm.tg_user.user_name,
            phone_number=phone_number,
            password=user_crm.password,
            uuid_user=user_uuid)
        ALL_SESSION[user_uuid] = user_bot
    logger.info(f'[GET] End EndPoint created_userbot. Params: [{user_uuid}]')

    if not await user_bot.is_authorized():
        await user_bot.send_code()
        return "UserBotCreatedNotAuthorized"
    asyncio.ensure_future(user_bot.get_all_user_channels())
    return "UserBotAuthorized"


@app.post('/authorized_userbot')
async def authorized_user_endpoint(request: UserAuthorized):
    logger.info(
        f'[POST] Start EndPoint authorized_userbot. Params: [{request.dict()}]')
    user_bot = ALL_SESSION.get(request.user_uuid)

    if user_bot is None:
        return f"UserBotNotFound"

    code_auth = request.code_auth
    if not code_auth:
        return "ErrorCodeAuthorized"

    result = await user_bot.sign_in(code_auth)

    if result == 'SessionPasswordNeededError':
        logger.error(
            f'[POST] End EndPoint authorized_userbot. User_bot needed password from user: [{request.user_uuid}]')
        return result

    elif result == 'PhoneCodeExpiredError':
        logger.error(
            f' [POST] End EndPoint authorized_userbot. User_bot сode compromised from user: [{request.user_uuid}]')
        ALL_SESSION.pop(request.user_uuid)
        return result

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint all_user_channels[user_bot is not authorized]. Params: [{request.user_uuid}]')
        return f"UserBotNotAuthorized"

    asyncio.ensure_future(user_bot.get_all_user_channels())
    return "UserBotCreatedAndAuthorized"
