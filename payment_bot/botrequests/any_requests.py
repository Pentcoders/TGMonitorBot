from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.dispatcher import FSMContext

from bot_init import dp
from utils import log_handler
from .bot_murkups import show_bot_menu


@dp.message_handler(content_types=ContentType.ANY, state='*')
@log_handler
async def cmd_show_logo(message: Message, state: FSMContext):
    await state.finish()
    await show_bot_menu(message)


@dp.callback_query_handler(state='*')
@log_handler
async def cmd_show_logo_cqh(call_back: CallbackQuery, state: FSMContext):
    await state.finish()
    await show_bot_menu(call_back.message)
