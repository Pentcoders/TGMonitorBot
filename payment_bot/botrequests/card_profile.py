from aiogram.dispatcher import FSMContext
from aiogram import types

from models import CardsMonitoring
from bot_init import dp, bot
from utils import log_handler
from utils.bot_state import (
                   StateBot,
                   SettingsCard_Profile,
                   ChangeTitleCard,
                   ChangeDescriptionCard,
                   DeleteCard_Monitoring,
                   DeleteYes,
                   DeleteNo)

from .card_murkups import (show_bot_card_menu,
                           change_profile_card)

from .userbot_api import stop_card_monitoring
from messages_bot import (INPUT_NEW_NAME_CARD,
                          BUG_MESSAGE,
                          INPUT_NEW_DESCRIPTION_CARD,
                          DELETE_QUESTION_CARD,
                          DELETE_CARD
                          )

@dp.callback_query_handler(SettingsCard_Profile(), state=StateBot.StateCards)
@log_handler
async def cmd_settings_card_profile(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    await change_profile_card(call_back.message, card)


@dp.callback_query_handler(ChangeTitleCard(), state=StateBot.StateChangeProfile)
@log_handler
async def cmd_settings_cahnge_title_card(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    async with state.proxy() as data:
        data['uuid_card'] = uuid_card

    await StateBot.StateChangeTitleCard.set()
    await call_back.message.answer(INPUT_NEW_NAME_CARD)


@dp.message_handler(content_types=['text'], state=StateBot.StateChangeTitleCard)
@log_handler
async def message_cahnge_title_card(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        uuid_card = data.get('uuid_card')
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

    await card.change_title(message.text)
    await change_profile_card(message, card)


@dp.callback_query_handler(ChangeDescriptionCard(), state=StateBot.StateChangeProfile)
@log_handler
async def cmd_settings_cahnge_decription_card(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    uuid_card: str = _info[1]
    async with state.proxy() as data:
        data['uuid_card'] = uuid_card

    await StateBot.StateChangeDescriptionCard.set()
    await call_back.message.answer(INPUT_NEW_DESCRIPTION_CARD)


@dp.message_handler(content_types=['text'], state=StateBot.StateChangeDescriptionCard)
@log_handler
async def message_cahnge_description_card(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        uuid_card = data.get('uuid_card')
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

    await card.change_description(message.text)
    await change_profile_card(message, card)
    

@dp.callback_query_handler(DeleteCard_Monitoring(), state=StateBot.StateChangeProfile)
@log_handler
async def cmd_delete_card(call_back: types.CallbackQuery, state: FSMContext):
    _info = call_back.data.split(':')
    async with state.proxy() as data:
        data['uuid_card'] = _info[1]

    yes_no = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton('Да', callback_data=f'delete:yes')
    no = types.InlineKeyboardButton('Нет', callback_data=f'delete:no')
    yes_no.row(yes, no)
    await StateBot.CardDelete.set()
    await call_back.message.edit_text(DELETE_QUESTION_CARD, reply_markup=yes_no)


@dp.callback_query_handler(DeleteYes(), state=StateBot.CardDelete)
@log_handler
async def cmd_delete_pattern_yes(call_back: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        uuid_card = data['uuid_card']
        data.clear()

    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    txt_card = f'card[{card.card_uuid}] {card.title}'
    result = await stop_card_monitoring(card.user_crm.uuid_user, [uuid_card])
    await card.delete()
    await show_bot_card_menu(call_back.message)
    
    if isinstance(result, str) and result.startswith('UserBotDeleteCard'):
        return await bot.answer_callback_query(
            call_back.id,
            text=DELETE_CARD.format(txt_card),
            show_alert=True)
    

@dp.callback_query_handler(DeleteNo(), state=StateBot.CardDelete)
@log_handler
async def cmd_delete_pattern_no(call_back: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        uuid_card = data['uuid_card']
        data.clear()

    card: CardsMonitoring = await CardsMonitoring.from_uuid(uuid_card)
    await change_profile_card(call_back.message, card)