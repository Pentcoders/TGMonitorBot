import aiohttp
import json
from loguru import logger


async def get_requests(URL: str, params: dict[str, str | int] = None) -> str:
    try:
        logger.info(f"[USER-API] Requser [GET] URL '{URL}' Params {params}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url=URL, params=params) as respons:
                result:str = await respons.json()
                if respons.status == 200:
                    logger.info(f"[USER-API] Respons [{URL}] status code: {respons.status}")
                    return result
                else:
                    logger.error(f"Respons [{URL}] status code: {respons.status} {result}")
    except aiohttp.ClientError as error:
        logger.exception(error)


async def post_requests(URL: str, data: json) -> str:
    try:
        logger.info(f"[USER-API] Requser [POST] URL '{URL}' Data {data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url=URL, json=data) as respons:
                result:str = await respons.json()
                if respons.status == 200:
                    logger.info(f"Respons [{URL}] status code: {respons.status} {result}")
                    return result
                else:
                    logger.error(f"Respons [{URL}] status code: {respons.status} {result}")
    except aiohttp.ClientError as error:
        logger.exception(error)
