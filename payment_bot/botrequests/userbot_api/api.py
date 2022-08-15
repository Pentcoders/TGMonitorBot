from loguru import logger
from pydantic import BaseModel

from .connector import get_requests, post_requests
from config import USERBOT_URL


class UserAuthorized(BaseModel):
    user_uuid: str
    code_auth: str


class PushingChannelSettings(BaseModel):
    user_uuid: str
    id_channel: str


class CardMonitoring(BaseModel):
    user_uuid: str
    card_uuid: str
    

class ManyCardsMonitoring(BaseModel):
    user_uuid: str
    card_uuid: list[str]


async def created_userbot(uuid_user: str) -> str:
    result:str = await get_requests(f'{USERBOT_URL}/created_userbot/{uuid_user}')
    logger.info(result)
    return result


async def update_user_channels(uuid_user: str):
    result = await get_requests(f'{USERBOT_URL}/update_user_channels/{uuid_user}')
    logger.info(result)
    return result

async def delete_cards(uuid_user: str):
    result = await get_requests(f'{USERBOT_URL}/delete_cards/{uuid_user}')
    logger.info(result)
    return result

async def create_signal_channels(uuid_user: str, card_uuid: str):
    card = CardMonitoring(user_uuid=str(uuid_user), card_uuid=str(card_uuid))
    result = await post_requests(f'{USERBOT_URL}/create_signal_channels',
                                 data=card.dict())
    logger.info(result)
    return result


async def health_check_user_bot(uuid_user: str):
    result = await get_requests(f'{USERBOT_URL}/health_check_user_bot/{uuid_user}')
    logger.info(result)
    return result


async def authorized_userbot(user_uuid: str, code_auth):
    user = UserAuthorized(user_uuid=user_uuid, code_auth=code_auth)
    result = await post_requests(f'{USERBOT_URL}/authorized_userbot',
                                 data=user.dict())
    logger.info(result)
    return result


async def stop_card_monitoring(user_uuid: str, cards_uuid: list[str]):
    card = ManyCardsMonitoring(user_uuid=str(user_uuid), card_uuid=cards_uuid)
    result = await post_requests(f'{USERBOT_URL}/stop_card_monitoring',
                                 data=card.dict())
    logger.info(result)
    return result


async def start_card_monitoring(user_uuid: str, cards_uuid: list[str]):
    card = ManyCardsMonitoring(user_uuid=str(user_uuid), card_uuid=cards_uuid)
    result = await post_requests(f'{USERBOT_URL}/start_card_monitoring',
                                 data=card.dict())
    logger.info(result)
    return result

async def health_check_card_monitoring(user_uuid: str, card_uuid: str):
    card = CardMonitoring(user_uuid=str(user_uuid), card_uuid=str(card_uuid))
    result = await post_requests(f'{USERBOT_URL}/health_check_card_monitoring',
                                 data=card.dict())
    logger.info(result)
    return result
