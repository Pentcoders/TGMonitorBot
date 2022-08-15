from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.exceptions import MessageError
from utils.bot_state import StateBot
from random import randint, shuffle
from messages_bot import ATTENTIONMESSAGE

async def show_inform_attention(message: Message):
    markup = inform_attention_text_markup()
    try:
        await message.delete()
    except MessageError:
        pass
    finally:
        await message.answer(ATTENTIONMESSAGE, parse_mode='HTML', reply_markup=markup)
    await StateBot.StateInformAttention.set()



def inform_attention_text_markup() -> InlineKeyboardMarkup:
    menu_markup = InlineKeyboardMarkup(row_width=2)
    random_code = str(randint(10000, 99999))
    code_valid = [
        InlineKeyboardButton(f"{random_code[:2]}-{random_code[2:]}", callback_data='btn_authorization'),
        InlineKeyboardButton(f"{random_code[:2]} {random_code[2:]}", callback_data='btn_bad_code'),
        InlineKeyboardButton(f"{random_code}", callback_data='btn_bad_code'),
    ]
    shuffle(code_valid)
    menu_markup.row(*code_valid)   
    return menu_markup