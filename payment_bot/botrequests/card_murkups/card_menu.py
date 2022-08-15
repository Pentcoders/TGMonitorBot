from functools import lru_cache
from aiogram.types import InlineKeyboardButton, Message
from utils.bot_state import StateBot
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited
from telegram_bot_pagination import InlineKeyboardPaginator
from models import CardsMonitoring, PatternMonitoring, ChannelsMonitoring
from ..bot_subutils import get_user_info_subscription, get_card_info
from ..userbot_api import stop_card_monitoring

from messages_bot import (
    BT_BACK,
    INFO_CREATE_CARD,
    BT_CREATE_CARD,
    BT_CARD_MONITORING,
    BT_CARD_OPTIONS,
    BT_CARD_PATTERN
)

async def show_bot_card_menu(message: Message, page: int = 1, *, card_uuid=None):
    cards: list[CardsMonitoring] = await get_card_info(message)
    size_card = await get_user_info_subscription(message)
    if size_card is None:
        return

    pg = page if page != -1 else len(cards)
    if card_uuid is not None:
        my_card = list(filter(lambda card: card.card_uuid==card_uuid, cards))[0]
        if my_card is not None:
            pg = cards.index(my_card) + 1
    page = pg
            
    paginator = InlineKeyboardPaginator(
        size_card[0],
        current_page=pg,
        data_pattern='card:{page}'
    )

    if len(cards) < pg:
        await empty_card(message, paginator)
    else:
        await complete_card(message, paginator, cards[pg-1], size_card)
    await StateBot.StateCards.set()


async def empty_card(message: Message, paginator: InlineKeyboardPaginator):
    paginator.add_before(InlineKeyboardButton(
        INFO_CREATE_CARD, callback_data='btn_create_card'))
    paginator.add_after(InlineKeyboardButton(
        BT_BACK, callback_data='btn_logo'))
    try:
        await message.edit_text(BT_CREATE_CARD, reply_markup=paginator.markup)
    except MessageNotModified:
        await message.answer(BT_CREATE_CARD, reply_markup=paginator.markup)
    except MessageCantBeEdited:
        await message.answer(BT_CREATE_CARD, reply_markup=paginator.markup)


async def complete_card(message: Message, paginator: InlineKeyboardPaginator, card: CardsMonitoring, size_card: tuple[int, int, int]):

    btn_monitoring_card = InlineKeyboardButton(
        BT_CARD_MONITORING, callback_data=f'btn_monitoring_card:{card.card_uuid}')
    btn_pattern_card = InlineKeyboardButton(
        BT_CARD_PATTERN, callback_data=f'btn_pattern_card:{card.card_uuid}')
    paginator.add_before(btn_monitoring_card, btn_pattern_card)

    paginator.add_after(InlineKeyboardButton(BT_BACK, callback_data=f'btn_logo'),
                        InlineKeyboardButton(BT_CARD_OPTIONS, callback_data=f'btn_profile_card:{card.card_uuid}'))

    text = await get_text_page(card, size_card)
    try:
        await message.edit_text(text, parse_mode='HTML', reply_markup=paginator.markup)
    except MessageNotModified:
        await message.answer(text, parse_mode='HTML', reply_markup=paginator.markup)
    except MessageCantBeEdited:
        await message.answer(text, parse_mode='HTML', reply_markup=paginator.markup)


async def get_text_page(card: CardsMonitoring, size_card: tuple[int, int, int]) -> str:
    monitoring: list[ChannelsMonitoring] = await ChannelsMonitoring.from_card(card)
    size_mc = f"[{len(monitoring)}/{size_card[1]}]"
    channel_monitoring = "\n".join(
        [
            f"\t{i}. {ch.channel_monitoring.title_channel_tg}" for i, ch in enumerate(monitoring, start=1)
        ]
    )

    pattern: list[PatternMonitoring] = await PatternMonitoring.from_card(card)
    size_pm = f"[{len(pattern)}/{size_card[2]}]"
    pattern_monitoring = "\n".join(
        [
            f"\t{i}) {ptt.pattern}" for i, ptt in enumerate(pattern, start=1)
        ]
    )
    if card.channel_pushing is not None:
        signal = card.channel_pushing.title_channel_tg    
    elif card.is_running:
        await card.update_status(False)
        result: str = await stop_card_monitoring(card.user_crm.uuid_user, [card.card_uuid])
        signal = '!NOT SET!'
    else:
        signal = '!NOT SET!'
    status = '🟢' if card.is_running else '🔴'
    text = "\n".join(
        [   
            f"{status} {card.title}",
            f"Назначение: {card.description}",
            f"Канал для сигналов: {signal}",
            f"Каналы мониторинга{size_mc}:",
            channel_monitoring,
            f"Паттерны мониторинга{size_pm}:",
            pattern_monitoring,
        ]
    )

    return text
