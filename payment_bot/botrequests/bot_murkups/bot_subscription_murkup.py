from aiogram import types
from aiogram.types import InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited

from models import Subscribtion
from messages_bot import (
    SUBSCRIPTION_ERROR,
    BT_PAYMENT_MENU_BUY_SUB,
    BT_BACK,
    
)

async def send_character_page_subscription(message: types.Message, page: int = 1):
    count_page = await Subscribtion.get_count_subscribtion()
    if count_page == 0:
        try:
            return await message.edit_text(SUBSCRIPTION_ERROR)
        except MessageNotModified:
            pass
        except MessageCantBeEdited:
            return await message.answer(SUBSCRIPTION_ERROR)
    
    subscribtion: Subscribtion = await Subscribtion.get_subscribtion_from_page(page-1)

    paginator = InlineKeyboardPaginator(
        count_page,
        current_page=page,
        data_pattern='character#{page}'
    )
    paginator.add_before(InlineKeyboardButton(BT_PAYMENT_MENU_BUY_SUB,
                                              callback_data=f'btn_payment:{subscribtion.api_subscriptions}'))

    paginator.add_after(InlineKeyboardButton(BT_BACK,
                                             callback_data='btn_logo'))
    try:
        await message.edit_text(await get_info_subscribtion(subscribtion),
                            reply_markup=paginator.markup,
                            parse_mode='Markdown')
    except MessageNotModified:
        pass
    except MessageCantBeEdited:
        await message.answer(await get_info_subscribtion(subscribtion),
                            reply_markup=paginator.markup,
                            parse_mode='Markdown')
 


async def get_info_subscribtion(subscribtion: Subscribtion) -> str:
    price = subscribtion.price / 100
    days = ''
    if str(subscribtion.term.days).endswith('1') and subscribtion.term.days > 20:
        days = f'{subscribtion.term.days} день'
    elif str(subscribtion.term.days).endswith(('2', '3', '4')):
        days = f'{subscribtion.term.days} дня'
    else:
        days = f'{subscribtion.term.days} дней'

    info = '\n'.join([
        subscribtion.title,
        f'{days} / {price}₽',
        subscribtion.description,
        f'Количество карточек мониторинга: {subscribtion.count_card_monitoring}',
        f'Каналов для мониторинга: {subscribtion.count_channels_monitoring}',
        f'Паттернов для мониторинга: {subscribtion.count_pattern_monitoring}'
    ])
    return info
