from aiogram.dispatcher import FSMContext
from aiogram import types

from bot_init import dp, bot
from utils import log_handler
from utils.bot_state import( StateBot,
                   StartMonitoringCard,
                   StopMonitoringCard,
                   InlineFilte)
from models import CardsMonitoring
from .userbot_api import start_card_monitoring, update_user_channels, stop_card_monitoring
from .bot_subutils import get_uuid_user_from_message
from .card_murkups import change_profile_card

from messages_bot import (NOT_AUTHORIZED_MESSAGE,
                          RUN_MONITORING_MESSAGE,
                          STOP_MONITORING_MESSAGE,
                          RUN_UPDATE_LIST_CHANNELS_MESSAGE,
                          BUG_MESSAGE)

@dp.callback_query_handler(StartMonitoringCard(), state=StateBot.StateChangeProfile)
@log_handler
async def cmd_settings_card_monitoring_start(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    uuid_user: str = await get_uuid_user_from_message(call_back.message)
    result: str = await start_card_monitoring(uuid_user, [uuid_card])
    card:CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    
    match result:
        case 'UserBotNotFound' | 'UserBotNotAuthorized':
            return await bot.answer_callback_query(
                call_back.id,
                text=NOT_AUTHORIZED_MESSAGE,
                show_alert=True)
        case 'UserBotStartCardMonitoring':
            await card.update_status(True)
            await bot.answer_callback_query(
                call_back.id,
                text=RUN_MONITORING_MESSAGE,
                show_alert=True)
        case _:
            return await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)

    await change_profile_card(call_back.message, card)

@dp.callback_query_handler(StopMonitoringCard(), state=StateBot.StateChangeProfile)
@log_handler
async def cmd_settings_card_monitoring_stop(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    uuid_user: str = await get_uuid_user_from_message(call_back.message)
    result: str = await stop_card_monitoring(uuid_user, [uuid_card])
    card:CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    match result:
        case 'UserBotNotFound' | 'UserBotNotAuthorized':
            return await bot.answer_callback_query(
                call_back.id,
                text=NOT_AUTHORIZED_MESSAGE,
                show_alert=True)
        case 'UserBotStopCardMonitoring':
            await card.update_status(False)
            await bot.answer_callback_query(
                call_back.id,
                text=STOP_MONITORING_MESSAGE,
                show_alert=True)
        case _:
            return await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)
    await change_profile_card(call_back.message, card)

@dp.callback_query_handler(InlineFilte('btn_update_channels'), state=StateBot.StateSettings)
@log_handler
async def cmd_create_card_monitoring(call_back: types.CallbackQuery, state: FSMContext):
    uuid_user: str = await get_uuid_user_from_message(call_back.message)
    result = await update_user_channels(uuid_user)
    match result:
        case 'UserBotNotFound' | 'UserBotNotAuthorized':
            return await bot.answer_callback_query(
                call_back.id,
                text=NOT_AUTHORIZED_MESSAGE,
                show_alert=True)
        case 'RunUpdateUserChannels':
            return await bot.answer_callback_query(
                call_back.id,
                text=RUN_UPDATE_LIST_CHANNELS_MESSAGE,
                show_alert=True)
        case _:
            return await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)
