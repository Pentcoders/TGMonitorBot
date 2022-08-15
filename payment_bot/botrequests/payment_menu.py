from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import LabeledPrice
from aiogram.types.message import ContentTypes

from bot_init import dp, bot, PURCHASED_SUBSCRIPTIONS
from utils import log_handler, log_payment
from utils.bot_state import StateBot, PaymentFilter
from models import Subscribtion, TGUsers, UserCRM, PurchasedSubscriptions
from config import PAYMENT_TOKEN

from .bot_subutils import user_is_authorized
from .bot_murkups import show_bot_menu, bot_successful_payment
from messages_bot import END_SUBSCRIPTION, CONGRATULATION_EXTENSION

@dp.callback_query_handler(PaymentFilter(), state=StateBot.StatePgSubscription)
@log_handler
async def payment_callback(call_back: types.CallbackQuery, state: FSMContext):
    api_subscriptions = call_back.data.split(':')[1]
    
    subscribtion: Subscribtion = await Subscribtion.get_subscribtion_from_api(api_subscriptions)
    
    start_parameter = str(subscribtion.title).lower().replace(' ', '-')
    price: list[LabeledPrice] = [LabeledPrice(
        subscribtion.title, subscribtion.price)]

    await bot.send_invoice(
        call_back.message.chat.id,
        title=subscribtion.title,
        description=subscribtion.description,
        provider_token=PAYMENT_TOKEN,
        currency='rub',
        is_flexible=False,
        prices=price,
        start_parameter=start_parameter,
        payload=subscribtion.api_subscriptions
    )
    await call_back.message.delete()


@dp.pre_checkout_query_handler(lambda query: True, state=StateBot.StatePgSubscription)
@log_handler
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT, state=StateBot.StatePgSubscription)
@log_payment
async def got_payment(message: types.Message, state: FSMContext):
    subscribtion = await Subscribtion.get_subscribtion_from_api(
        message.successful_payment.invoice_payload
    )
    user_tg = await TGUsers.from_message(message)
    await set_user_crm_subscription(user_tg, subscribtion)
    
    if await user_is_authorized(message):
        await message.answer('🎉')
        await message.answer(CONGRATULATION_EXTENSION)
        return await show_bot_menu(message)
    
    await bot_successful_payment(message)


async def set_user_crm_subscription(user_tg: TGUsers, subscription: Subscribtion):
    user_crm = await UserCRM.from_tg_user(user_tg)
    if user_crm is None:
        user_crm = await UserCRM.add_user_crm(user_tg)
    await PurchasedSubscriptions.set_purchased_subscription(user_crm, subscription)
    await user_crm.set_authorized(True)
    
    PURCHASED_SUBSCRIPTIONS.update(await PurchasedSubscriptions.get_all_purchased_subscription())
    return user_crm


async def check_purchased_subscription():
    data_now = datetime.utcnow()
    for chat_id, purch in PURCHASED_SUBSCRIPTIONS.items():
        delta:timedelta = purch.date_end_subscriptions.replace(tzinfo=None) - data_now
        if delta < timedelta(seconds=1):
            await purch.user_crm.set_authorized(False)
            continue
        elif delta < timedelta(7):
            days = ""
            if delta.days == 1:
                days = '1 день'
            elif 1 < delta.days <= 4:
                days = f'{delta.days} дня'
            else:
                days = f'{delta.days} дней'
            await bot.send_message(chat_id, END_SUBSCRIPTION.format(days))
