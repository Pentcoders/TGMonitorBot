from loguru import logger
import asyncio
from bot_init import app, ALL_SESSION


@app.get('/update_user_channels/{user_uuid}')
async def update_user_channels(user_uuid: str):
    logger.info(
        f'[GET] Start EndPoint update_user_channels. Params: [user: {user_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)
    if not user_bot:
        logger.info(
            f'[GET] End EndPoint update_user_channels. Params: [user: {user_uuid}]')
        return f"UserBotNotFound"

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint update_user_channels. Params: [user: {user_uuid}]')
        return f"UserBotNotAuthorized"

    asyncio.ensure_future(user_bot.get_all_user_channels())
    logger.info(
        f'[GET] End EndPoint update_user_channels. Params: [user: {user_uuid}]')
    return f"RunUpdateUserChannels"