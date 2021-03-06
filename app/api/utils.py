"""
See the NOTICE file distributed with this work for additional information
regarding copyright ownership.


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import logging

import aiohttp
from aiohttp import ContentTypeError
from fastapi import HTTPException

from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]


async def find_result_url(session, url, headers):
    """
    Send a request to metadata URL to check status. status: 200 will return url otherwise it will cancel to coroutine job and return "".
    session: aiohttp session
    url: metadata url
    """
    try:
        async with session.get(url[1], headers=headers) as response:
            if response.status == 200:
                url_result = url[0]

    except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
        asyncio.current_task().remove_done_callback(asyncio.current_task)
        asyncio.current_task().cancel()
        url_result = ""
    return url_result


async def create_request_coroutine(url_list, url_path, headers, params):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result.
    url_list [(tuple)]: Metadata URL list
    """
    try:
        async with aiohttp.ClientSession(
            raise_for_status=True, read_timeout=None
        ) as session:
            coroutines = [
                asyncio.ensure_future(
                    find_result_url(session=session, url=url, headers=headers)
                )
                for url in url_list
            ]
            done, pending = await asyncio.wait(coroutines)
            result = ""
            for task in done:
                if not task.cancelled():
                    url = task.result()
                    async with session.get(
                        url=url + url_path, headers=headers, params=params
                    ) as response:
                        if response.status == 200:

                            if response.headers.get("content-type").find("text") != -1:
                                return await response.text()
                            else:
                                return await response.json()

            return result

    except (ContentTypeError, Exception) as e:
        return HTTPException(status_code=406)
