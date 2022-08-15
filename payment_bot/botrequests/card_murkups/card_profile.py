from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited

from utils.bot_state import StateBot
from models import CardsMonitoring
from messages_bot import (
    BT_CARD_OPTION_NAME,
BT_CARD_OPTION_DESC,
BT_CARD_OPTION_STOP,
BT_CARD_OPTION_START,
BT_CARD_OPTION_DELETE,
BT_BACK
)

async def change_profile_card(message: Message, card: CardsMonitoring):
    change_profile_card_markup = InlineKeyboardMarkup()

    # btn_pushing_card = InlineKeyboardButton(
    #     'Канал для сигналов', callback_data=f'btn_pushing_card:{card.card_uuid}')
    # change_profile_card_markup.add(btn_pushing_card)
    
    btn_change_title = InlineKeyboardButton(
        BT_CARD_OPTION_NAME, callback_data=f'btn_CT:{card.card_uuid}')   
    btn_change_description = InlineKeyboardButton(
        BT_CARD_OPTION_DESC, callback_data=f'btn_CD:{card.card_uuid}')
    change_profile_card_markup.row(btn_change_title, btn_change_description)

    if card.is_running:
        btn_stop_monitoring = InlineKeyboardButton(
            BT_CARD_OPTION_STOP, callback_data=f'btn_StopM:{card.card_uuid}')
        change_profile_card_markup.row(btn_stop_monitoring)
    else:
        btn_start_monitoring = InlineKeyboardButton(
            BT_CARD_OPTION_START, callback_data=f'btn_StartM:{card.card_uuid}')
        change_profile_card_markup.add(btn_start_monitoring)
        
    btn_delete_card = InlineKeyboardButton(
        BT_CARD_OPTION_DELETE, callback_data=f'btn_delete_card:{card.card_uuid}')
    change_profile_card_markup.add(btn_delete_card)
    
    btn_card_monitoring = InlineKeyboardButton(
        BT_BACK, callback_data='btn_card_monitoring')
    change_profile_card_markup.add(btn_card_monitoring)
    
    if card.channel_pushing is not None:
        signal = card.channel_pushing.title_channel_tg    
    else:
        signal = '!NOT SET!'
    
    info_card = '\n'.join(
        [   
            f"Название <b>Карточки</b>: {card.title}",
            f"Назначение: {card.description}",
            f"Канал для сигналов: {signal}",
            '🟢 Мониторинг запущен' if card.is_running else '🔴 Мониторинг остановлен'
        ]
    )

    await StateBot.StateChangeProfile.set()

    try:
        await message.edit_text(info_card, parse_mode='HTML', reply_markup=change_profile_card_markup)
    except MessageNotModified:
        pass
    except MessageCantBeEdited:
        await message.answer(info_card, parse_mode='HTML', reply_markup=change_profile_card_markup)
