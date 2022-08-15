from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import CardsMonitoring, UserChannels, ChannelsMonitoring, PatternMonitoring, UserCRM
from bot_init import dp, bot
from utils import log_handler
from utils.bot_state import (
                   StateBot,
                   InlineFilte,
                   CardPage,
                   SettingsCard_Monitoring,
                   SettingsCard_Pattern,
                   MonitoringChannelChoise,
                   MonitoringChannelPage,
                   PatternPage,
                   PatternChange,
                   PatternCreate,
                   PatternDescription,
                   CommandShowMonitoring,
                   PatternDelete, DeleteYes, DeleteNo)

from .card_murkups import (show_bot_card_menu,
                           show_monitoring_channels,
                           show_pattern_monitoring)

from .bot_subutils import get_user_info_subscription
from .userbot_api import start_card_monitoring, create_signal_channels
from messages_bot import (SUCCESSFUL_CREATE_CARD,
                          ERROR_MESSAGE,
                          BUG_MESSAGE,
                          CHOICE_MAX_COUNT_CHANNEL,
                          UPDATE_LIST_CHANNELS,
                          INPUT_NEW_PATTERN,
                          CHOICE_MAX_COUNT_PATTERN,
                          DELETE_QUESTION_PATTERN,
                          DELETE_PATTERN,
                          NOT_AUTHORIZED_MESSAGE)

@dp.message_handler(CommandShowMonitoring(), state='*')
@log_handler
async def cmd_get_card_monitoring_message(message: types.Message, state: FSMContext):
    await show_bot_card_menu(message)


@dp.callback_query_handler(InlineFilte('btn_card_monitoring'), state='*')
@log_handler
async def cmd_get_card_monitoring_callback(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    card_uuid = None
    if len(_info) > 1:
        card_uuid = _info[1]
        return await show_bot_card_menu(call_back.message, card_uuid=card_uuid)
    
    await show_bot_card_menu(call_back.message)


@dp.callback_query_handler(CardPage(), state=StateBot.StateCards)
@log_handler
async def characters_page_callback_subscription(call_back: types.CallbackQuery, state: FSMContext):
    page = int(call_back.data.split(':')[1])
    await show_bot_card_menu(call_back.message, page)


@dp.callback_query_handler(InlineFilte('btn_create_card'), state=StateBot.StateCards)
@log_handler
async def cmd_create_card_monitoring(call_back: types.CallbackQuery, state: FSMContext):
    user = await UserCRM.from_message(call_back.message)
    card = await CardsMonitoring.create_card(user)
    result:dict = await create_signal_channels(user.uuid_user, card.card_uuid)
    
    match result.get('status'):
        case 'Ok':
            await bot.answer_callback_query(
                call_back.id,
                text=SUCCESSFUL_CREATE_CARD,
                show_alert=True)
            return await show_bot_card_menu(call_back.message, -1)
        case 'Error':
            await bot.answer_callback_query(
                call_back.id,
                text=ERROR_MESSAGE.format(result.get("result")),
                show_alert=True)
            await card.delete()
        case _:
            await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)
            await card.delete()
            

@dp.callback_query_handler(SettingsCard_Monitoring(), state=StateBot.StateCards)
@log_handler
async def cmd_settings_card_monitoring(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    await show_monitoring_channels(call_back.message, card)


@dp.callback_query_handler(MonitoringChannelPage(), state=StateBot.StateChoiseMonitoring)
@log_handler
async def cmd_page_choise_monitoring_channel(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    page = int(_info[2])
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    await show_monitoring_channels(call_back.message, card, page)


@dp.callback_query_handler(MonitoringChannelChoise(), state=StateBot.StateChoiseMonitoring)
@log_handler
async def cmd_choise_monitoring_channel(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    page = int(_info[1])
    uuid_card: str = _info[2]
    id_user_channel = int(_info[3])

    channel:UserChannels = await UserChannels.from_id_channel(id_user_channel)
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)

    result = await ChannelsMonitoring.add_or_pop_channel(card, channel)
    if isinstance(result, str) and result == 'StorageIsTaken':
        return await bot.answer_callback_query(
            call_back.id,
            text=CHOICE_MAX_COUNT_CHANNEL,
            show_alert=True)
    
    if card.is_running:
        await update_card(call_back, channel.user_crm.uuid_user, card.card_uuid, UPDATE_LIST_CHANNELS)
    else:
        await bot.answer_callback_query(
            call_back.id,
            text=UPDATE_LIST_CHANNELS,
            show_alert=True)
    await show_monitoring_channels(call_back.message, card, page)


@dp.callback_query_handler(SettingsCard_Pattern(), state=StateBot.StateCards)
@log_handler
async def cmd_settings_card_pattern(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)

    await show_pattern_monitoring(call_back.message, card)


@dp.callback_query_handler(PatternPage(), state=StateBot.StatePatterns)
@log_handler
async def cmd_settings_card_pattern_page(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    page = int(_info[2])
    await show_pattern_monitoring(call_back.message, card, page)


@dp.callback_query_handler(PatternCreate(), state=StateBot.StatePatterns)
@dp.callback_query_handler(PatternChange(), state=StateBot.StatePatterns)
@log_handler
async def cmd_settings_card_pattern_input(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    async with state.proxy() as data:
        data['uuid_card'] = _info[1]
        if len(_info) > 2:
            data['id_pattern'] = int(_info[2])

    await StateBot.StatePatternInput.set()
    await call_back.message.answer(INPUT_NEW_PATTERN)


@dp.message_handler(content_types=['text'], state=StateBot.StatePatternInput)
@log_handler
async def cmd_settings_card_pattern_create(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        uuid_card = data.get('uuid_card')
        id_pattern = data.get('id_pattern')

        data.clear()
    if uuid_card is None or not isinstance(uuid_card, str):
        # Warning
        await message.answer(BUG_MESSAGE)
        return await show_bot_card_menu(message)

    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    if card is None:
        # Warning
        await message.answer(BUG_MESSAGE)
        return await show_bot_card_menu(message)
    txt_ptt = message.text.split(', ')
    if id_pattern is not None:
        pattern: PatternMonitoring = await PatternMonitoring.from_id_pattern(id_pattern)
        await pattern.change_pattern(message.text)
    else:
        size_card = await get_user_info_subscription(message)
        for ppt in txt_ptt:
            result = await PatternMonitoring.add_pattern(card,  size_card[2], ppt)
            if result is None:
                await message.answer(CHOICE_MAX_COUNT_PATTERN)
                break
    if card.is_running:
        await update_card(message, card.channel_pushing.user_crm.uuid_user, card.card_uuid)

    await show_pattern_monitoring(message, card, -1)


@dp.callback_query_handler(PatternDelete(), state=StateBot.StatePatterns)
@log_handler
async def cmd_delete_pattern(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    async with state.proxy() as data:
        data['uuid_card'] = _info[1]
        data['id_pattern'] = int(_info[2])

    yes_no = InlineKeyboardMarkup()
    yes = InlineKeyboardButton('Да', callback_data=f'delete:yes')
    no = InlineKeyboardButton('Нет', callback_data=f'delete:no')
    yes_no.row(yes, no)
    await StateBot.PatternDelete.set()
    await call_back.message.edit_text(DELETE_QUESTION_PATTERN, reply_markup=yes_no)


@dp.callback_query_handler(DeleteYes(), state=StateBot.PatternDelete)
@log_handler
async def cmd_delete_pattern_yes(call_back: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        id_pattern = data['id_pattern']
        uuid_card = data['uuid_card']
        data.clear()
    pattern: PatternMonitoring = await PatternMonitoring.from_id_pattern(id_pattern)
    pattern_txt = pattern.pattern
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    await pattern.delete()
    
    if card.is_running:
        await update_card(call_back, card.channel_pushing.user_crm.uuid_user, card.card_uuid, DELETE_PATTERN.format(pattern_txt))
        
    await show_pattern_monitoring(call_back.message, card)

@dp.callback_query_handler(DeleteNo(), state=StateBot.PatternDelete)
@log_handler
async def cmd_delete_pattern_no(call_back: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        id_pattern = data['id_pattern']

    pattern: PatternMonitoring = await PatternMonitoring.from_id_pattern(id_pattern)
    card = pattern.card_monitoring
    await show_pattern_monitoring(call_back.message, card)


@dp.callback_query_handler(PatternDescription(), state=StateBot.StatePatterns)
@log_handler
async def cmd_settings_card_pattern_decription_input(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    async with state.proxy() as data:
        data['uuid_card'] = _info[1]
        data['id_pattern'] = int(_info[2])

    await StateBot.StatePatternChangeDescr.set()
    await call_back.message.answer('Введите описание паттерна мониторинга:')


@dp.message_handler(content_types=['text'], state=StateBot.StatePatternChangeDescr)
@log_handler
async def cmd_settings_card_pattern_cahnge_decription(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        uuid_card = data.get('uuid_card')
        id_pattern = int(data.get('id_pattern'))
        data.clear()

    if uuid_card is None or not isinstance(uuid_card, str):
        # Warning
        await message.answer(BUG_MESSAGE)
        return await show_bot_card_menu(message)

    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    if card is None:
        # Warning
        await message.answer(BUG_MESSAGE)
        return await show_bot_card_menu(message)

    if id_pattern is None:
        await message.answer(BUG_MESSAGE)
        return await show_bot_card_menu(message)

    pattern: PatternMonitoring = await PatternMonitoring.from_id_pattern(id_pattern)
    await pattern.change_description(message.text)
    
    if card.is_running:
        await update_card(message, card.channel_pushing.user_crm.uuid_user, card.card_uuid)
    await show_pattern_monitoring(message, card)

async def update_card(call_back: types.CallbackQuery|types.Message, user_uuid, card_uuid, info:str=None):
    result: str = await start_card_monitoring(user_uuid, [card_uuid])
    if isinstance(call_back, types.Message):
        return
    match result:
        case 'UserBotNotFound' | 'UserBotNotAuthorized':
            await bot.answer_callback_query(
                call_back.id,
                text=NOT_AUTHORIZED_MESSAGE,
                show_alert=True)
        case 'UserBotStartCardMonitoring':
            await bot.answer_callback_query(
            call_back.id,
            text=info,
            show_alert=True)
        case _:
            await bot.answer_callback_query(
                call_back.id,
                text=BUG_MESSAGE,
                show_alert=True)
    return result