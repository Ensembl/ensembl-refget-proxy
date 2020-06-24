import asyncio
import logging

import aiohttp
from loguru import logger

from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]


async def find_result_url(session, url):
    """
    Send a request to metadata URL to check status. status: 200 will return url otherwise it will cancel to coroutine job and return "".
    session: aiohttp session
    url: metadata url
    """
    try:
        async with session.get(url[1]) as response:
            if response.status == 200:
                url_result = url[0]

    except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
        asyncio.current_task().remove_done_callback(asyncio.current_task)
        asyncio.current_task().cancel()
        url_result = ""

    return url_result


async def create_request_coroutine(url_list, query_string=""):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result.
    url_list [(tuple)]: Metadata URL list
    """
    try:
        async with aiohttp.ClientSession(
            raise_for_status=True, read_timeout=None
        ) as session:
            coroutines = [
                asyncio.ensure_future(find_result_url(session, url)) for url in url_list
            ]
            done, pending = await asyncio.wait(coroutines)
            result = ""
            for task in done:
                if not task.cancelled():
                    url = task.result()
                    async with session.get(url + query_string) as response:
                        if response.status == 200:
                            if response.headers.get("content-type").find("text") != -1:
                                return await response.text()
                            else:
                                return await response.json()
            return result
    except Exception as e:
        logger.log("INFO", "Unhandled exception in create_request_coroutine" + str(e))
