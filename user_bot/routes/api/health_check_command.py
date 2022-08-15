from loguru import logger

from bot_init import app, ALL_SESSION
from ..schema import CardMonitoring


@app.get('/health_check_user_bot/{user_uuid}')
async def health_check_user_bot(user_uuid: str):
    logger.info(
        f'[GET] Start EndPoint health_check_user_bot. Params: [user: {user_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)
    if not user_bot:
        logger.info(
            f'[GET] End EndPoint health_check_user_bot. Params: [user: {user_uuid}]')
        return f"UserBotNotFound"

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint health_check_user_bot. Params: [user: {user_uuid}]')
        return f"UserBotNotAuthorized"

    logger.info(
        f'[GET] End EndPoint health_check_user_bot. Params: [user: {user_uuid}]')
    return f"UserBotLaunched"


@app.get('/health_check_card_monitoring')
async def health_check_card_monitoring(request: CardMonitoring):
    user_uuid = request.user_uuid
    card_uuid = request.card_uuid
    logger.info(
        f'[GET] Start EndPoint health_check_card_monitoring. Params: [user: {user_uuid}, card: {card_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)
    if not user_bot:
        logger.info(
            f'[GET] End EndPoint health_check_card_monitoring. Params: [user: {user_uuid}, card: {card_uuid}]')
        return f"UserBotNotFound"

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint health_check_card_monitoring. Params: [user: {user_uuid}, card: {card_uuid}]')
        return f"UserBotNotAuthorized"

    result = await user_bot.health_check_card_monitoring(card_uuid)
    if isinstance(result, str):
        logger.info(
            f'[GET] End EndPoint health_check_card_monitoring. Params: [user: {user_uuid}, card: {card_uuid}]')
        return result

    logger.info(
        f'[GET] End EndPoint health_check_card_monitoring. Params: [user: {user_uuid}, card: {card_uuid}]')
    return f"BadRequest"
