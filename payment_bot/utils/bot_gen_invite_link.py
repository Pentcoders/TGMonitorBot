from aiogram import Bot


async def get_invite_link(bot: Bot, api_refer: str) -> str:
    me_bot = await bot.get_me()
    return f"https://t.me/{me_bot.username}?start={api_refer}"
