
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited
from telegram_bot_pagination import InlineKeyboardPaginator

from utils.bot_state import StateBot
from models import CardsMonitoring, PatternMonitoring
from ..bot_subutils import get_user_info_subscription
from messages_bot import (BT_BACK, 
                          BT_PATTERN_CREATE,
                          BT_PATTERN_CHANGE,
                          BT_PATTERN_DELETE)

async def show_pattern_monitoring(message: Message, card:CardsMonitoring, page: int = 1):
    patterns = await PatternMonitoring.from_card(card)
    size_card = await get_user_info_subscription(message)
    if size_card is None:
        return

    data_pattern_page = f'pattern:{card.card_uuid}:'+'{page}'
    pg = page if page != -1 else len(patterns)
    
    paginator = InlineKeyboardPaginator(
        size_card[2],
        current_page=pg,
        data_pattern=data_pattern_page
    )

    if len(patterns) < pg:
        info = await get_all_patterns_info(patterns, size_card[2])
        await empty_pattern(message, paginator, card, info)
    else:
        info = await get_all_patterns_info(patterns, size_card[2], patterns[pg-1])
        await complete_pattern(message, paginator, patterns[pg-1], card, info)
    await StateBot.StatePatterns.set()


async def empty_pattern(message: Message, paginator: InlineKeyboardPaginator, card:CardsMonitoring, info_message:str):
    paginator.add_before(InlineKeyboardButton(
        BT_PATTERN_CREATE, callback_data=f'btn_CrPtt:{card.card_uuid}'))
    paginator.add_after(InlineKeyboardButton(
        BT_BACK, callback_data=f'btn_card_monitoring:{card.card_uuid}'))
    try:
        await message.edit_text(info_message, reply_markup=paginator.markup, parse_mode='Markdown')
    except MessageNotModified:
        pass
    except MessageCantBeEdited:
        await message.answer(info_message, reply_markup=paginator.markup, parse_mode='Markdown')


async def complete_pattern(message: Message, paginator: InlineKeyboardPaginator, pattern: PatternMonitoring, card: CardsMonitoring, info_message:str):

    btn_change_pattern = InlineKeyboardButton(
        BT_PATTERN_CHANGE, callback_data=f'btn_ChPtt:{card.card_uuid}:{pattern.id_pattern}')
    # btn_change_description_pattern = InlineKeyboardButton(
    #     '🪛 Назначение', callback_data=f'btn_ChDescPtt:{card.card_uuid}:{pattern.id_pattern}')
    btn_delete_pattern = InlineKeyboardButton(
        BT_PATTERN_DELETE, callback_data=f'btn_DeletePtt:{card.card_uuid}:{pattern.id_pattern}')
    # paginator.add_before(btn_change_pattern, btn_change_description_pattern, btn_delete_pattern)
    paginator.add_before(btn_change_pattern, btn_delete_pattern)

    paginator.add_after(InlineKeyboardButton(BT_BACK, callback_data=f'btn_card_monitoring:{card.card_uuid}'))

    try:
        await message.edit_text(info_message, reply_markup=paginator.markup, parse_mode='Markdown')
    except MessageNotModified:
        pass
    except MessageCantBeEdited:
        await message.answer(info_message, reply_markup=paginator.markup, parse_mode='Markdown')



async def get_text_page(pattern: PatternMonitoring) -> str:
    text = "\n".join(
        [
            f"Паттерн: {pattern.pattern}",
            # f"Назначение: {pattern.description}",
        ]
    )
    return text



async def get_all_patterns_info(all_patterns: list[PatternMonitoring], chunks:int, coise_pattern:PatternMonitoring=None) -> str:
    info = []
    size_patterns = len(all_patterns)
    for index, pattern in enumerate(all_patterns, start=1):
        if coise_pattern is None:
            info.append(f"{index}) {pattern.pattern}")
        elif pattern.pattern == coise_pattern.pattern:
            info.append(f"👉🏼 *{pattern.pattern}*")
        else:
            info.append(f"{index}) {pattern.pattern}")
    
    if len(all_patterns) != chunks-1:
        not_undef = len(all_patterns) + 1
        info.append(f"_{not_undef} - {chunks} Not Undefined_")
                        
    return "\n".join(info)
