from loguru import logger

from bot_init import app, ALL_SESSION
from ..schema import ManyCardsMonitoring, CardMonitoring


@app.get('/delete_cards/{user_uuid}')
async def delete_card_endpoint(user_uuid: str):
    logger.info(
        f'[GET] Start EndPoint delete_card. Params: [user: {user_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)

    if not user_bot:
        logger.info(
            f'[GET] End EndPoint delete_card. Params: [user: {user_uuid}]')
        return f"UserBotNotFound"

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint delete_card. Params: [user: {user_uuid}]')
        return f"UserBotNotAuthorized"

    await user_bot.drop_cards()

    logger.info(
        f'[GET] End EndPoint delete_card. Params: [user: {user_uuid}]')
    return f"UserBotDeleteCard"


@app.post('/start_card_monitoring')
async def start_card_monitoring_endpoint(request: ManyCardsMonitoring):
    user_uuid = request.user_uuid
    cards_uuid: list[str] = request.card_uuid
    logger.info(
        f'[GET] Start EndPoint start_card_monitoring Params: [user: {user_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)

    if not user_bot:
        logger.info(
            f'[GET] End EndPoint start_card_monitoring. Params: [user: {user_uuid}]')
        return "UserBotNotFound"

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint start_card_monitoring. Params: [user: {user_uuid}]')
        return "UserBotNotAuthorized"
    
    await user_bot.start_card_monitoring()
    for card in cards_uuid:
        await user_bot.update_card_monitoring(card)
        
    logger.info(
        f'[GET] End EndPoint start_card_monitoring. Params: [user: {user_uuid}]')
    return "UserBotStartCardMonitoring"


@app.post('/stop_card_monitoring')
async def stop_card_monitoring_endpoint(request: ManyCardsMonitoring):
    user_uuid = request.user_uuid
    cards_uuid = request.card_uuid
    logger.info(
        f'[GET] Start EndPoint stop_card_monitoring. Params: [user: {user_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)

    if not user_bot:
        logger.info(
            f'[GET] End EndPoint stop_card_monitoring. Params: [user: {user_uuid}]')
        return "UserBotNotFound"

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint stop_card_monitoring. Params: [user: {user_uuid}]')
        return "UserBotNotAuthorized"
    
    for card in cards_uuid:
        await user_bot.stop_card_monitoring(card)

    logger.info(
        f'[GET] End EndPoint stop_card_monitoring. Params: [user: {user_uuid}]')
    return "UserBotStopCardMonitoring"


@app.post('/create_signal_channels')
async def create_card_monitoring_endpoint(request: CardMonitoring):
    user_uuid = request.user_uuid
    card_uuid = request.card_uuid
    logger.info(
        f'[GET] Start EndPoint create_card_monitoring. Params: [user: {user_uuid}]')
    user_bot = ALL_SESSION.get(user_uuid)

    if not user_bot:
        logger.info(
            f'[GET] End EndPoint create_card_monitoring. Params: [user: {user_uuid}]')
        return {'status': 'Error', 'result': 'UserBotNotFound'} 

    if not await user_bot.is_authorized():
        logger.info(
            f'[GET] End EndPoint create_card_monitoring. Params: [user: {user_uuid}]')
        return {'status': 'Error', 'result': 'UserBotNotAuthorized'} 
    # 
    result = await user_bot.card_configuration(card_uuid)
    # 
    logger.info(
        f'[GET] End EndPoint create_card_monitoring. Params: [user: {user_uuid}]')
    return {'status': 'Ok' if result is not None else 'Error', 'result': result if result is not None else 'ErrorCreatedChannelPushing'}