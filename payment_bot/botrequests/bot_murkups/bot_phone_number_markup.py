from functools import lru_cache
from aiogram.types import ReplyKeyboardMarkup, Message, KeyboardButton
from aiogram.utils.exceptions import MessageError

from utils.bot_state import StateBot
from messages_bot import SEND_PHONE_NUMBER

async def bot_send_phone_number(message: Message):
    try:
        await message.delete()
    except MessageError:
        pass
    finally:
        await StateBot.StatePhoneNumber.set()
        await message.answer(SEND_PHONE_NUMBER, reply_markup=bot_send_phone_number_murkup())


@lru_cache
def bot_send_phone_number_murkup() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = KeyboardButton(
        text="Отправить номер телефона", request_contact=True)
    keyboard.add(button_phone)
    return keyboard
