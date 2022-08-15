from aiogram import types
from aiogram.types import InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator

from models import Subscribtion
from messages_bot import (
    BT_PAYMENT_MENU_BUY_SUB,
    BT_PAYMENT_MENU_DESCRIPTION_SUB)

async def send_character_page_subscription(message: types.Message, page: int = 1):
    count_page = await Subscribtion.get_count_subscribtion()
    subscribtion: Subscribtion = await Subscribtion.get_subscribtion_from_page(page-1)

    paginator = InlineKeyboardPaginator(
        count_page,
        current_page=page,
        data_pattern='character#{page}'
    )
    paginator.add_before(InlineKeyboardButton(BT_PAYMENT_MENU_BUY_SUB, callback_data=f'btn_payment:{subscribtion.api_subscriptions}'),
                         InlineKeyboardButton(BT_PAYMENT_MENU_DESCRIPTION_SUB, callback_data='btn_agreement'))

    paginator.add_after(InlineKeyboardButton(
        'Назад', callback_data='btn_logo'))

    await message.edit_text(await get_info_subscribtion(subscribtion),
                            reply_markup=paginator.markup,
                            parse_mode='Markdown')


async def get_info_subscribtion(subscribtion: Subscribtion) -> str:
    price = subscribtion.price / 100
    days = ''
    if subscribtion.term.days == 1:
        days = '1 день'
    elif 1 < subscribtion.term.days <= 4:
        days = f'{subscribtion.term.days} дня'
    else:
        days = f'{subscribtion.term.days} дней'

    info = '\n'.join([
        subscribtion.title,
        f'{days} / {price}',
        subscribtion.description,
        f'Каналов для информирования: {subscribtion.count_channels_pushing}',
        f'Каналов для мониторинга: {subscribtion.count_channels_monitoring}',
        f'Паттернов для мониторинга: {subscribtion.count_pattern_monitoring}'
    ])
    return info
