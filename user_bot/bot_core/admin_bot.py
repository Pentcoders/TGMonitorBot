import aiohttp
from loguru import logger
from config import TELEGRAM_TOKEN_SEND_BOT

async def admin_send_message(chat_id, text):
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN_SEND_BOT}/{method}"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "html"}
    try:
        logger.info(f"[USER-API] Requser [POST] URL '{url}'")
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=data) as respons:
                result = await respons.json()
                if respons.status == 200:
                    logger.info(
                        f"Respons [{url}] status code: {respons.status}")
                    return result
                else:
                    logger.error(f"Respons [{url}] status code: {respons.status} {result}")
    except aiohttp.ClientError as error:
        logger.exception(error)