from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from aiogram.dispatcher import FSMContext

from bot_init import dp
from utils import log_handler
from utils.bot_state import InlineFilte, StateBot, CommandBuySubscription
from models import TGUsers
from .bot_murkups import show_bot_menu, send_character_page_subscription


@dp.message_handler(CommandStart(), state='*')
@log_handler
async def cmd_start(message: types.Message, state: FSMContext):
    user_tg = await TGUsers.from_message(message)
    command: list[str] = message.text.split()
    if len(command) > 1:
        await user_tg.set_api_refer(command[1])
    await show_bot_menu(message)


@dp.callback_query_handler(InlineFilte('btn_logo'), state='*')
@log_handler
async def cmd_logo(call_back: types.CallbackQuery, state: FSMContext):
    await show_bot_menu(call_back.message)


@dp.message_handler(CommandBuySubscription(), state='*')
@log_handler
async def cmd_buy_subscription(message: types.Message, state: FSMContext):
    await StateBot.StatePgSubscription.set()
    await send_character_page_subscription(message)
