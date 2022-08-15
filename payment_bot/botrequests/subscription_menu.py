from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_init import dp
from utils import log_handler
from utils.bot_state import StateBot, SubscriptionPage
from .bot_murkups import send_character_page_subscription


@dp.callback_query_handler(SubscriptionPage(), state=StateBot.StatePgSubscription)
@log_handler
async def characters_page_callback_subscription(call_back: types.CallbackQuery, state: FSMContext):
    page = int(call_back.data.split('#')[1])
    await send_character_page_subscription(call_back.message, page)
