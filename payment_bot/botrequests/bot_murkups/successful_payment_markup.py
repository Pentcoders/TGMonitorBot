from functools import lru_cache
from aiogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton

from utils.bot_state import StateBot
from messages_bot import CONGRATULATION_EXTENSION

async def bot_successful_payment(message: Message):
    await StateBot.StatePhoneNumber.set()
    await message.answer('🎉')
    await message.answer(CONGRATULATION_EXTENSION, parse_mode='Markdown', reply_markup=bot_successful_payment_markup())

@lru_cache
def bot_successful_payment_markup() -> InlineKeyboardMarkup:
    further_markup = InlineKeyboardMarkup(row_width=2)

    btn_back = InlineKeyboardButton('Назад', callback_data='btn_logo')
    btn_further = InlineKeyboardButton('Далее', callback_data='btn_phone_number')
    further_markup.row(btn_back, btn_further)

    return further_markup
