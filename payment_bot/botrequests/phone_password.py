from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_init import dp
from utils import log_handler
from utils.bot_state import  StateBot, InlineFilte
from models import UserCRM
from .bot_murkups import (bot_send_phone_number,
                          bot_send_password,
                          show_bot_menu,
                          show_inform_attention,
                          bot_send_password_question)

from messages_bot import BUG_MESSAGE


@dp.callback_query_handler(InlineFilte('btn_phone_number'), state=StateBot.StateSettings)
@dp.callback_query_handler(InlineFilte('btn_phone_number'), state=StateBot.StatePhoneNumber)
async def cmd_phone_number(call_back: types.CallbackQuery, state: FSMContext):
    await bot_send_phone_number(call_back.message)


@dp.message_handler(content_types=['contact'], state=StateBot.StatePhoneNumber)
@log_handler
async def cmd_get_phone_number(message: types.Message, state: FSMContext):
    if message.contact is None:
        await message.answer(BUG_MESSAGE)
        return await show_bot_menu(message)

    user_crm: UserCRM = await UserCRM.from_message(message)
    await user_crm.set_phone_number(message.contact)
    await bot_send_password_question(message)


@dp.callback_query_handler(InlineFilte('send_password_yes'), state=StateBot.StateEnterPasswordYesOrNo)
async def cmd_yes_no_send_password(call_back: types.CallbackQuery, state: FSMContext):
    await bot_send_password(call_back.message)


@dp.message_handler(content_types=['text'], state=StateBot.StateEnterPassword)
@log_handler
async def cmd_get_password(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer(BUG_MESSAGE)
        return await show_bot_menu(message)

    user_crm: UserCRM = await UserCRM.from_message(message)
    await user_crm.set_password(message.text)
    await show_inform_attention(message)


@dp.callback_query_handler(InlineFilte('send_password_no'), state=StateBot.StateEnterPasswordYesOrNo)
@log_handler
async def cmd_no_password(call_back: types.CallbackQuery, state: FSMContext):
    await show_inform_attention(call_back.message)
