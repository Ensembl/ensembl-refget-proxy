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
import json
import logging

from aiohttp import ClientResponseError
from fastapi import APIRouter, Request, responses
from loguru import logger

from api.error_response import response_error_handler
from api.utils import create_request_coroutine
from core.logging import InterceptHandler
from core.redis import get_cached_metadata

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()


@router.get("/{checksum}", name="sequence", response_class=responses.PlainTextResponse)
async def get_sequence(request: Request, checksum: str):
    """
    Return Refget sequence based on a sequence checksum.
    """
    params = request.query_params
    headers = {header: request.headers.get(header) for header in request.headers}
    url_path = "sequence/" + checksum

    try:
        result = await create_request_coroutine(
            checksum=checksum, url_path=url_path, headers=headers, params=params,
        )
        if result["status"] == 200:
            return responses.Response(result["response"], headers=result["headers"])
        else:
            return response_error_handler(result)

    except (ClientResponseError, Exception) as e:
        logger.log("DEBUG", e)


@router.get("/{checksum}/metadata", name="sequence:metadata")
async def get_sequence_metadata(request: Request, checksum: str):
    """
    Return Refget sequence metadata based on a sequence checksum.
    """

    url_path = "sequence/" + checksum + "/metadata"
    result = await get_cached_metadata(checksum + "/metadata")
    headers = {"content": "application/json"}

    if result:
        return responses.Response(json.dumps(result), headers=headers, status_code=200)

    try:
        params = request.query_params
        headers = {header: request.headers.get(header) for header in request.headers}

        result = await create_request_coroutine(
            checksum=checksum, url_path=url_path, headers=headers, params=params,
        )

        if result["status"] != 200:
            return response_error_handler(result)
        else:
            return responses.Response(
                json.dumps(result["response"]), headers=result["headers"]
            )

    except (ClientResponseError, Exception) as e:

        logger.log("DEBUG", e)
