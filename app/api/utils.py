#
#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

import asyncio
import logging

import aiohttp
from aiohttp import ClientResponseError, ClientConnectorError
from loguru import logger

from core.config import REFGET_SERVER_URL_LIST
from core.logging import InterceptHandler
from core.redis import cache_metadata, cache_url, get_cached_url

logging.getLogger().handlers = [InterceptHandler()]


def metadata_url_list(checksum):
    """
    Create and return a list of dictionary containing:
    [{"refget_server_url": "Refget server URL", "checksum": "checksum", "metadata_url": "Generated metadata URL")]
    """

    url_list = []
    for url in REFGET_SERVER_URL_LIST:
        if not url.endswith("/"):
            url = url + "/"
        url_list.append(
            {
                "refget_server_url": url,
                "checksum": checksum,
                "metadata_url": url + "sequence/" + checksum + "/metadata",
            }
        )
    return url_list


async def find_result_url(session, url_detail):
    """
    Send a request to metadata URL to check status. status: 200 will return url otherwise it will cancel to coroutine job and return "".
    session: aiohttp session
    url: metadata url
    """

    try:
        # async with session.trace(url_detail["metadata_url"]) as trace:
        #     logger.log('DEBUG', trace)
        async with session.get(url_detail["metadata_url"]) as response:
            if response.status == 200:
                await cache_url(url_detail=url_detail)
                url_result = url_detail

    except (ClientResponseError, ClientConnectorError) as e:
        asyncio.current_task().remove_done_callback(asyncio.current_task)
        asyncio.current_task().cancel()
        url_result = ""

    return url_result


async def on_request_start(
        session, trace_config_ctx, params):
    logger.log('DEBUG', "Starting request")
    logger.log('DEBUG', params)
    logger.log('DEBUG', "----------")
    try:
        for i in params.headers:
            if i.start('x') != -1:
                params.headers.pop(i)
    except:
        pass
    logger.log('DEBUG', params.headers)
    # params.headers = {'accept': '*/*', 'host': params.headers.get('host')}


async def on_request_end(session, trace_config_ctx, params):
    logger.log('DEBUG', session)
    logger.log('DEBUG', params)
    logger.log('DEBUG', "Ending request")


async def create_request_coroutine(checksum, url_path, headers, params):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result.
    url_list [(tuple)]: Metadata URL list
    """
    try:
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        url_detail = await get_cached_url(checksum)
        async with aiohttp.ClientSession(
                raise_for_status=True, read_timeout=None, trust_env=True, trace_configs=[trace_config]
        ) as session:
            if url_detail is None:
                url_list = metadata_url_list(checksum)

                coroutines = [
                    asyncio.ensure_future(find_result_url(session=session, url_detail=url_detail))
                    for url_detail in url_list
                ]
                done, pending = await asyncio.wait(coroutines)
                for task in done:
                    if not task.cancelled():
                        url_detail = task.result()

            return await get_result(
                url_detail=url_detail,
                session=session,
                url_path=url_path,
                headers=headers,
                params=params,
            )

    except Exception as e:
        logger.log("DEBUG", "UNHANDLED EXCEPTION" + str(e))


async def get_result(url_detail, session, url_path, headers, params):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result.
    """
    response_dict = {"response": "", "headers": {}, "status": 404}

    if url_detail:
        try:
            async with session.get(
                    url=url_detail["refget_server_url"] + url_path,
                    params=params,
                    headers=headers,
                    ssl=False,
            ) as response:
                if response.status == 200:
                    response_dict["headers"] = response.headers
                    response_dict["status"] = response.status
                    if response.headers.get("content-type").find("text") != -1:
                        response_dict["response"] = await response.text()
                    else:
                        response_dict["response"] = await response.json()
                        await cache_metadata(url_detail=url_detail, metadata=response_dict["response"])

                    return response_dict
                else:
                    response_dict["status"] = response.status
        except ClientResponseError as client_error:
            response_dict["status"] = client_error.status

    return response_dict
