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
import re

import aiohttp
from aiohttp import ClientResponseError, ClientConnectorError
from loguru import logger

from core.config import REFGET_SERVER_URL_LIST, HTTP_PROXY, HTTPS_PROXY
from core.logging import InterceptHandler
from core.redis import cache_metadata, cache_url, get_cached_url

logging.getLogger().handlers = [InterceptHandler()]


def is_url_valid(url):
    if url.find(".") and url != "http://test.service.refget.review.ensembl.org/":
        return True
    else:
        return False


def metadata_url_list(checksum):
    """
    Create and return a list of dictionary containing:
    [{"refget_server_url": "Refget server URL", "checksum": "checksum", "metadata_url": "Generated metadata URL"), is_url:Boolean]
    is_url: To define a proxy rule in our k8s structure and route the internal services directly to the related service.
    """

    url_list = []
    for url in REFGET_SERVER_URL_LIST:
        url = url.strip()
        if not url.endswith("/"):
            url = url + "/"

        url_list.append(
            {
                "refget_server_url": url,
                "checksum": checksum,
                "metadata_url": url + "sequence/" + str(checksum) + "/metadata",
                "is_url": is_url_valid(url),
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

        if url_detail["is_url"]:

            async with session.get(
                    url_detail["metadata_url"],
                    proxy=HTTP_PROXY
            ) as response:
                if response.status == 200:
                    await cache_url(url_detail=url_detail)
                    url_result = url_detail
        else:

            async with session.get(url_detail["metadata_url"]) as response:
                if response.status == 200:
                    await cache_url(url_detail=url_detail)
                    url_result = url_detail

    except (ClientResponseError, ClientConnectorError) as e:
        asyncio.current_task().remove_done_callback(asyncio.current_task)
        asyncio.current_task().cancel()
        url_result = {}

    return url_result


async def create_request_coroutine(checksum, url_path, headers, params):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result.
    url_list [(tuple)]: Metadata URL list
    """
    try:

        url_detail = await get_cached_url(checksum)
        async with aiohttp.ClientSession(
                raise_for_status=True, read_timeout=None
        ) as session:
            if url_detail == {}:
                url_list = metadata_url_list(checksum)

                coroutines = [
                    asyncio.ensure_future(
                        find_result_url(session=session, url_detail=url_detail)
                    )
                    for url_detail in url_list
                ]
                done, pending = await asyncio.wait(coroutines)
                for task in done:
                    if not task.cancelled():
                        url_detail = task.result()
            if url_detail.get("is_url"):
                return await get_result_proxy(
                    url_detail=url_detail,
                    session=session,
                    url_path=url_path,
                    headers=headers,
                    params=params,
                )
            else:
                return await get_result(
                    url_detail=url_detail,
                    session=session,
                    url_path=url_path,
                    headers=headers,
                    params=params,
                )

    except Exception as e:
        logger.log("DEBUG", "UNHANDLED EXCEPTION: " + str(e))


async def get_result_proxy(url_detail, session, url_path, headers, params):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result using a proxy service.
    """
    response_dict = {"response": "", "headers": {}, "status": 404}

    if url_detail != {}:
        try:
            async with session.get(
                    url=url_detail["refget_server_url"] + url_path,
                    params=params,
                    headers=headers,
                    proxy=HTTP_PROXY
            ) as response:
                if response.status == 200:
                    response_dict["headers"] = response.headers
                    response_dict["status"] = response.status
                    if response.headers.get("content-type").find("text") != -1:
                        response_dict["response"] = await response.text()
                    else:
                        response_dict["response"] = await response.json()
                        await cache_metadata(
                            url_detail=url_detail, metadata=response_dict["response"]
                        )

                    return response_dict
                else:
                    response_dict["status"] = response.status

        except ClientResponseError as client_error:
            response_dict["status"] = client_error.status

    return response_dict


async def get_result(url_detail, session, url_path, headers, params):
    """
    Create coroutine requests with asyncio to return Refget result based on metadata result.
    """
    response_dict = {"response": "", "headers": {}, "status": 404}

    if url_detail != {}:
        try:
            async with session.get(
                    url=url_detail["refget_server_url"] + url_path,
                    params=params,
                    ssl=False,
                    headers=headers,
            ) as response:
                if response.status == 200:
                    response_dict["headers"] = response.headers
                    response_dict["status"] = response.status
                    if response.headers.get("content-type").find("text") != -1:
                        response_dict["response"] = await response.text()
                    else:
                        response_dict["response"] = await response.json()
                        await cache_metadata(
                            url_detail=url_detail, metadata=response_dict["response"]
                        )

                    return response_dict
                else:
                    response_dict["status"] = response.status
        except ClientResponseError as client_error:
            response_dict["status"] = client_error.status

    return response_dict
