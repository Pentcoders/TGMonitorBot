from math import ceil

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.exceptions import MessageNotModified
from utils.bot_state import StateBot
from loguru import logger
from telegram_bot_pagination import InlineKeyboardPaginator
from models import UserChannels, CardsMonitoring
from ..bot_subutils import get_all_user_cahnnels, get_monitoring_channels
from messages_bot import (BT_LIST_CHANNELS_EMPTY,
                          BT_BACK,
                          BT_LIST_CHANNELS_CHOISE)

async def show_monitoring_channels(message: Message, card: CardsMonitoring, page: int = 1):
    channels: list[UserChannels] = await get_all_user_cahnnels(message)
    if card.channel_pushing in channels:
        channels.pop(channels.index(card.channel_pushing))

    if len(channels) == 0:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            BT_BACK, callback_data=f'btn_card_monitoring:{card.card_uuid}'))
        return await message.edit_text(BT_LIST_CHANNELS_EMPTY, reply_markup=markup)

    size_pages = ceil(len(channels) / 5)
    data_pattern_page = f'monitoring_ch:{card.card_uuid}:'+'{page}'
    paginator = InlineKeyboardPaginator(
        size_pages,
        current_page=page,
        data_pattern=data_pattern_page)

    logger.info(f'Run :{page=}')
    if size_pages <= 1:
        await coise_channels(message, paginator, channels, card, page)
    else:
        await coise_channels(message, paginator, channels[(page-1)*5:page*5], card, page)
    await StateBot.StateChoiseMonitoring.set()


async def coise_channels(message: Message, paginator: InlineKeyboardPaginator, channels: list[UserChannels], card: CardsMonitoring, page: int):
    if not isinstance(channels, list):
        return
    
    monitoring_cahnnels = await get_monitoring_channels(message, card.id_card)
    for channel in channels:
        info_ch = channel.title_channel_tg if channel not in monitoring_cahnnels else f'✅ {channel.title_channel_tg}'
        paginator.add_before(InlineKeyboardButton(
            info_ch, callback_data=f'btn_CMC:{page}:{card.card_uuid}:{channel.id_user_channel}'))
    logger.info(f'btn_card_monitoring:{page}')
    btn_card_monitoring = InlineKeyboardButton(
        BT_BACK, callback_data=f'btn_card_monitoring:{card.card_uuid}')

    paginator.add_after(btn_card_monitoring)
    try:
        await message.edit_text(BT_LIST_CHANNELS_CHOISE, reply_markup=paginator.markup)
    except MessageNotModified as error:
        pass