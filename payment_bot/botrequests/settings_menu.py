from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_init import dp, bot
from models import CardsMonitoring, UserCRM
from utils import log_handler
from utils.bot_state import  StateBot, InlineFilte, CommandShowSettings
from .bot_murkups import show_bot_settings
from .bot_subutils import get_card_info
from .userbot_api import start_card_monitoring, stop_card_monitoring, delete_cards

from messages_bot import (BUG_MESSAGE,
                          EMPTY_LIST_CARD,
                          ALL_RUN_CARD,
                          NOT_AUTHORIZED_MESSAGE,
                          ALL_STOP_CARD_QUESTION,
                          ALL_STOP_CARD,
                          ALL_RUN_CARD_QUESTION)


@dp.message_handler(CommandShowSettings(), state='*')
@log_handler
async def cmd_buy_subscription(message: types.Message, state: FSMContext):
    await show_bot_settings(message)


@dp.callback_query_handler(InlineFilte('btn_settings'), state='*')
@dp.callback_query_handler(InlineFilte('stop_monitoring_no'), state='*')
@dp.callback_query_handler(InlineFilte('start_monitoring_no'), state='*')
@log_handler
async def cmd_settings_callback(call_back: types.CallbackQuery, state: FSMContext):
    await show_bot_settings(call_back.message)


@dp.callback_query_handler(InlineFilte('btn_start_monitoring'), state=StateBot.StateSettings)
@log_handler
async def cmd_start_monitoring_callback(call_back: types.CallbackQuery, state: FSMContext):
    cards: list[CardsMonitoring] = await get_card_info(call_back.message)
    if isinstance(cards, list) and len(cards) == 0:
        await bot.answer_callback_query(
            call_back.id,
            text=EMPTY_LIST_CARD,
            show_alert=True)
        return await show_bot_settings(call_back.message)
    run = list(filter(lambda card: not card.is_running, cards))
    if len(run) == 0:
        await bot.answer_callback_query(
            call_back.id,
            text=ALL_RUN_CARD,
            show_alert=True)
        return await show_bot_settings(call_back.message)
    info = [ALL_RUN_CARD_QUESTION]
    data_run: list[str] = []
    for i, card in enumerate(run, start=1):
        data_run.append(str(card.card_uuid))
        info.append(
            f'{i}) {card.title} [id{card.card_uuid}]'
        )
    yes_no = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(
        'Да', callback_data=f'start_monitoring_yes')
    no = types.InlineKeyboardButton(
        'Нет', callback_data=f'start_monitoring_no')
    yes_no.row(yes, no)
    async with state.proxy() as data:
        data['run_cards'] = ':'.join(data_run)

    await StateBot.StateStartAllMontoringCards.set()
    await call_back.message.edit_text('\n'.join(info), reply_markup=yes_no)


@dp.callback_query_handler(InlineFilte('start_monitoring_yes'), state=StateBot.StateStartAllMontoringCards)
@log_handler
async def cmd_start_monitoring_callback_yes(call_back: types.CallbackQuery, state: FSMContext):
    cards: list[CardsMonitoring] = await get_card_info(call_back.message)
    run = list(filter(lambda card: not card.is_running, cards))

    user_crm = await UserCRM.from_message(call_back.message)
    result = await start_card_monitoring(user_crm.uuid_user, [str(card.card_uuid) for card in run])
    await show_bot_settings(call_back.message)
    match result:
        case 'UserBotNotFound' | 'UserBotNotAuthorized':
            return await bot.answer_callback_query(
                call_back.id,
                text=NOT_AUTHORIZED_MESSAGE,
                show_alert=True)
        case 'UserBotStartCardMonitoring':
            for card in run:
                await card.update_status(True)
            return await bot.answer_callback_query(
                call_back.id,
                text=ALL_RUN_CARD,
                show_alert=True)
        case _:
            return await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)


@dp.callback_query_handler(InlineFilte('btn_stop_monitoring'), state=StateBot.StateSettings)
@log_handler
async def cmd_stop_monitoring_callback(call_back: types.CallbackQuery, state: FSMContext):
    cards: list[CardsMonitoring] = await get_card_info(call_back.message)
    if isinstance(cards, list) and len(cards) == 0:
        await bot.answer_callback_query(
            call_back.id,
            text=EMPTY_LIST_CARD,
            show_alert=True)
        return await show_bot_settings(call_back.message)
    stoped = list(filter(lambda card: card.is_running, cards))
    if len(stoped) == 0:
        await bot.answer_callback_query(
            call_back.id,
            text=ALL_STOP_CARD,
            show_alert=True)
        return await show_bot_settings(call_back.message)
    info = [ALL_STOP_CARD_QUESTION]
    data_run: list[str] = []
    for i, card in enumerate(stoped, start=1):
        data_run.append(str(card.card_uuid))
        info.append(
            f'{i}) {card.title} [id{card.card_uuid}]'
        )
    yes_no = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(
        'Да', callback_data=f'stop_monitoring_yes')
    no = types.InlineKeyboardButton(
        'Нет', callback_data=f'stop_monitoring_no')
    yes_no.row(yes, no)
    async with state.proxy() as data:
        data['run_cards'] = ':'.join(data_run)

    await StateBot.StateStopAllMontoringCards.set()
    await call_back.message.edit_text('\n'.join(info), reply_markup=yes_no)


@dp.callback_query_handler(InlineFilte('stop_monitoring_yes'), state=StateBot.StateStopAllMontoringCards)
@log_handler
async def cmd_stop_monitoring_callback_yes(call_back: types.CallbackQuery, state: FSMContext):
    cards: list[CardsMonitoring] = await get_card_info(call_back.message)
    stoped = list(filter(lambda card: card.is_running, cards))

    user_crm = await UserCRM.from_message(call_back.message)
    result = await stop_card_monitoring(user_crm.uuid_user, [str(card.card_uuid) for card in stoped])
    await show_bot_settings(call_back.message)
    await delete_cards(user_crm.uuid_user)
    match result:
        case 'UserBotNotFound' | 'UserBotNotAuthorized':
            return await bot.answer_callback_query(
                call_back.id,
                text=NOT_AUTHORIZED_MESSAGE,
                show_alert=True)
        case 'UserBotStopCardMonitoring':
            for card in stoped:
                await card.update_status(False)
            return await bot.answer_callback_query(
                call_back.id,
                text=ALL_STOP_CARD,
                show_alert=True)
        case _:
            return await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)
            
