from datetime import datetime
from aiogram import types
from bot_init import bot, PURCHASED_SUBSCRIPTIONS
from sqlalchemy.future import select

from models.database import async_session
from models import (PurchasedSubscriptions, 
                    Subscribtion,
                    UserCRM,
                    TGUsers,
                    CardsMonitoring,
                    UserChannels, 
                    ChannelsMonitoring)


async def anti_throttled(*args, **kwargs):
    if isinstance(args[0], types.CallbackQuery):
        call_back = args[0]
        await bot.answer_callback_query(
            call_back.id,
            text='Слишком частый запрос',
            show_alert=True)

    if isinstance(args[0], types.Message):
        message = args[0]
        await message.answer('Слишком частый запрос')


async def user_is_subscribed(message: types.Message) -> bool:
    user = message.from_user
    if user.is_bot:
        user = message.chat
    async with async_session() as session:
        result = await session.execute(
            select(PurchasedSubscriptions).
            join(UserCRM).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id)
        )
        sub: PurchasedSubscriptions = result.scalars().one_or_none()
        if sub is None:
            return False
        return True


async def user_is_authorized(message: types.Message) -> bool:
    user = message.from_user
    if user.is_bot:
        user = message.chat
    async with async_session() as session:
        result = await session.execute(
            select(UserCRM.is_authorized).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id)
        )
        udb: bool = result.scalars().one_or_none()
        return udb

async def get_user_info_subscription(message: types.Message) -> tuple[int, int, int]:
    user = message.from_user
    if user.is_bot:
        user = message.chat
    async with async_session() as session:
        result = await session.execute(
            select(Subscribtion).
            join(PurchasedSubscriptions).
            join(UserCRM).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id)
        )
        sub: Subscribtion = result.scalars().one_or_none()
        if sub is None:
            return None
        return sub.count_card_monitoring, sub.count_channels_monitoring, sub.count_pattern_monitoring


async def get_card_info(message: types.Message) -> list[CardsMonitoring]:
    user = message.from_user
    if user.is_bot:
        user = message.chat
    async with async_session() as session:
        result = await session.execute(
            select(CardsMonitoring).
            join(UserCRM).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id).
            order_by(CardsMonitoring.id_card)
        )
        return result.scalars().all()


async def get_channels_creator(message: types.Message) -> list[UserChannels]:
    user = message.from_user
    if user.is_bot:
        user = message.chat
        
    async with async_session() as session:
        result = await session.execute(
            select(UserChannels).
            join(UserCRM).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id,
                  UserChannels.is_creator == True).
            order_by(UserChannels.title_channel_tg)
        )
        return result.scalars().all()


async def get_pushing_channels(message: types.Message) -> list[UserChannels]:
    cards: list[CardsMonitoring] = await get_card_info(message)
    return [card.channel_pushing for card in cards]


async def get_all_user_cahnnels(message: types.Message) -> list[UserChannels]:
    user = message.from_user
    if user.is_bot:
        user = message.chat
        
    async with async_session() as session:
        result = await session.execute(
            select(UserChannels).
            join(UserCRM).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id).
            order_by(UserChannels.title_channel_tg)
        )
        return result.scalars().all()


async def get_monitoring_channels(message: types.Message, id_card:int) -> list[UserChannels]:
    user = message.from_user
    if user.is_bot:
        user = message.chat
        
    async with async_session() as session:
        result = await session.execute(
            select(ChannelsMonitoring).
            join(CardsMonitoring).
            join(UserChannels).
            join(UserCRM).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id,
                  CardsMonitoring.id_card == id_card)
        )
        channels: list[ChannelsMonitoring] = result.scalars().all()
    
    return [channel.channel_monitoring for channel in channels]


async def get_uuid_user_from_message(message: types.Message) -> str:
    user = message.from_user
    if user.is_bot:
        user = message.chat
        
    async with async_session() as session:
        result = await session.execute(
            select(UserCRM.uuid_user).
            join(TGUsers).
            where(TGUsers.id_user_tg == user.id))
        return str(result.scalars().one_or_none())