from functools import lru_cache
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageError

from utils.bot_state import StateBot
from messages_bot import PASSWORD_QUESTION, INPUT_PASSWORD_MESSAGE

async def bot_send_password_question(message: Message):
    try:
        await message.delete()
    except MessageError:
        pass
    finally:
        await StateBot.StateEnterPasswordYesOrNo.set()
        await message.answer(PASSWORD_QUESTION, reply_markup=send_password_markup())

async def bot_send_password(message: Message):
    try:
        await message.delete()
    except MessageError:
        pass
    finally:
        await StateBot.StateEnterPassword.set()
        await message.answer(INPUT_PASSWORD_MESSAGE, reply_markup=ReplyKeyboardRemove())

@lru_cache
def send_password_markup():
    yes_or_no = InlineKeyboardMarkup()
    btn_send_password_yes = InlineKeyboardButton('Да', callback_data='send_password_yes')
    btn_send_password_no = InlineKeyboardButton('Нет', callback_data='send_password_no')
    yes_or_no.row(btn_send_password_no, btn_send_password_yes)
    return yes_or_no