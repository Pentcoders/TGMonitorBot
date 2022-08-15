from functools import lru_cache
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import MessageError

from ..bot_subutils import user_is_subscribed
from utils.bot_state import StateBot
from messages_bot import (PREVIEW_MESSAGE,
                          BUY_SUBSCRIPTION,
                          MAIN_MENU_MESSAGE,
                          BUTTON_BUY_SUBSCRIPTION,
                          BUTTON_HELP,
                          BUTTON_SUPPORT,
                          BUTTON_REBUY_SUBSCRIPTION,
                          BUTTON_SETTINGS,
                          BUTTON_MONITORING)


async def show_bot_menu(message: Message):
    if not await user_is_subscribed(message):
        try:
            await message.delete()
        except MessageError:
            pass
        finally:
            await message.answer(PREVIEW_MESSAGE,
                                        reply_markup=bot_keyboard_markup_not_sub())
            return await message.answer(BUY_SUBSCRIPTION,
                                        reply_markup=bot_keyboard_markup_not_sub()) 

    await StateBot.StateLogo.set()

    try:
        await message.delete()
    except MessageError:
        pass
    finally:
        await message.answer(MAIN_MENU_MESSAGE,
                             reply_markup=bot_keyboard_markup_sub())


@lru_cache
def bot_keyboard_markup_not_sub() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(BUTTON_BUY_SUBSCRIPTION)
    ).add(
        KeyboardButton(BUTTON_HELP),
        KeyboardButton(BUTTON_SUPPORT)
    )
    return keyboard


@lru_cache
def bot_keyboard_markup_sub() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton(BUTTON_MONITORING),
    ).add(
        KeyboardButton(BUTTON_SETTINGS),
        KeyboardButton(BUTTON_REBUY_SUBSCRIPTION)
    ).add(
        KeyboardButton(BUTTON_HELP),
        KeyboardButton(BUTTON_SUPPORT)
    )
    return keyboard


# @lru_cache
# def bot_menu_markup() -> InlineKeyboardMarkup:
#     menu_markup = InlineKeyboardMarkup(row_width=3)

#     btn_subscription = InlineKeyboardButton(
#         'Выбрать подписку', callback_data='btn_subscription')
#     menu_markup.add(btn_subscription)

    # btn_profile = InlineKeyboardButton('Профиль', callback_data='btn_profile')
    # btn_settings = InlineKeyboardButton(
    #     'Настройки', callback_data='btn_settings')
    # menu_markup.row(btn_profile, btn_settings)
    # menu_markup.add(btn_settings)

    # btn_referral = InlineKeyboardButton(
    #     'Реффералка', callback_data='btn_referral')
    # btn_reviews = InlineKeyboardButton(
    #     'Отзывы', callback_data='btn_reviews', url='')
    # btn_service = InlineKeyboardButton(
    #     'О сервисе', callback_data='btn_service')
    # menu_markup.row(btn_referral, btn_reviews, btn_service)

    # btn_service = InlineKeyboardButton(
    #     'Тех поддержка', callback_data='btn_service')
    # menu_markup.add(btn_service)

    # return menu_markup
