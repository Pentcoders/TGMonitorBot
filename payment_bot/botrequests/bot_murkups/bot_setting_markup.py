from functools import lru_cache
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited

from utils.bot_state import StateBot
from messages_bot import (
    BT_SETTINGS_AUTHORIZED,
    BT_SETTINGS_UPDATE_CHANNELS,
    BT_SETTINGS_STOP_ALL_CARD,
    BT_SETTINGS_RUN_ALL_CARD,
    BT_BACK,
    INFO_SETTINGS_MENU
)

async def show_bot_settings(message: Message):
    try:
        await message.edit_text(INFO_SETTINGS_MENU, reply_markup=bot_menu_settings_accessible())
    except MessageNotModified:
        pass
    except MessageCantBeEdited:
        await message.answer(INFO_SETTINGS_MENU, reply_markup=bot_menu_settings_accessible())
    await StateBot.StateSettings.set()


@lru_cache
def bot_menu_settings_accessible() -> InlineKeyboardMarkup:
    menu_markup = InlineKeyboardMarkup(row_width=2)

    btn_authorization = InlineKeyboardButton(
        BT_SETTINGS_AUTHORIZED, callback_data='btn_phone_number')
    menu_markup.add(btn_authorization)
    
    btn_update_channels = InlineKeyboardButton(
        BT_SETTINGS_UPDATE_CHANNELS, callback_data='btn_update_channels')
    menu_markup.add(btn_update_channels)
    
    btn_update_channels = InlineKeyboardButton(
        BT_SETTINGS_RUN_ALL_CARD, callback_data='btn_start_monitoring')
    menu_markup.add(btn_update_channels)
    
    btn_update_channels = InlineKeyboardButton(
        BT_SETTINGS_STOP_ALL_CARD, callback_data='btn_stop_monitoring')
    menu_markup.add(btn_update_channels)

    btn_back = InlineKeyboardButton(BT_BACK, callback_data='btn_logo')
    menu_markup.add(btn_back)

    return menu_markup
