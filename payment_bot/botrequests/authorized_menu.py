from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_init import dp, bot
from utils import log_handler
from utils.bot_state import StateBot, InlineFilte
from models import UserCRM
from .bot_murkups import show_bot_menu
from .userbot_api import created_userbot, authorized_userbot

from messages_bot import (SEND_CODE_AUTHORIZED,
                          FORMAT_INPUTE_CODE,
                          SUCCESSFUL_AUTHORIZATION,
                          FLOODWAIT_MESSAGE,
                          BUG_MESSAGE,
                          BAD_AUTHORIZATION_MASSEGE,
                          BAD_CODE_AUTHORIZATION_MASSEGE,
                          TWO_FACTOR_BAD_MESSAGE,
                          USERBOT_BAD_MESSAGE,
                          SUCCESSFUL_AUTHORIZATION_USERBOT)

@dp.callback_query_handler(InlineFilte('btn_authorization'), state=StateBot.StateInformAttention)
@log_handler
async def cmd_authorization(call_back: types.CallbackQuery, state: FSMContext):
    user_crm: UserCRM = await UserCRM.from_message(call_back.message)
    result:str = await created_userbot(user_crm.uuid_user)

    match result:
        case 'UserBotCreatedNotAuthorized':
            await StateBot.StateSendCodeAuthorized.set()
            await bot.answer_callback_query(
                call_back.id,
                text=FORMAT_INPUTE_CODE,
                show_alert=True)      
            return await call_back.message.edit_text(SEND_CODE_AUTHORIZED)
        
        case 'UserBotAuthorized':
            await bot.answer_callback_query(
                call_back.id,
                text=SUCCESSFUL_AUTHORIZATION,
                show_alert=True) 
            
        case 'FloodWaitError':
            await bot.answer_callback_query(
                call_back.id,
                text=FLOODWAIT_MESSAGE,
                show_alert=True)
        case _:
            await call_back.message.answer(BUG_MESSAGE)
        
    await show_bot_menu(call_back.message)


@dp.callback_query_handler(InlineFilte('btn_bad_code'), state=StateBot.StateInformAttention)
@log_handler
async def cmd_inform_bad_code(call_back: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(
        call_back.id,
        text=BAD_AUTHORIZATION_MASSEGE,
        show_alert=True)


@dp.message_handler(content_types=['text'], state=StateBot.StateSendCodeAuthorized)
@log_handler
async def cmd_get_code_authorized(message: types.Message, state: FSMContext):
    code = message.text
    if code is None:
        return await message.edit_text(BUG_MESSAGE)

    if code.count('-') != 1:
        return await message.answer(BAD_CODE_AUTHORIZATION_MASSEGE)

    code = code.split('-')
    if len(code) != 2:
        return await message.answer(BAD_CODE_AUTHORIZATION_MASSEGE)

    code = ''.join(code)
    user_crm: UserCRM = await UserCRM.from_message(message)

    result = await authorized_userbot(str(user_crm.uuid_user), code)
    if result == 'UserBotCreatedAndAuthorized':
        await user_crm.set_authorized(True)
    await message.answer(check_authorized_userbot(result))
    await show_bot_menu(message)


def check_authorized_userbot(result: str):
    match result:
        case 'PhoneCodeExpiredError':
            return BAD_CODE_AUTHORIZATION_MASSEGE

        case 'SessionPasswordNeededError':
            return TWO_FACTOR_BAD_MESSAGE
        
        case 'UserBotNotFound':
            return USERBOT_BAD_MESSAGE

        case 'ErrorCodeAuthorized':
            return 'Ошибка кода авторизации'

        case 'UserBotCreatedAndAuthorized' | 'UserBotAuthorized':
            return SUCCESSFUL_AUTHORIZATION_USERBOT

        case _:
            return BUG_MESSAGE
