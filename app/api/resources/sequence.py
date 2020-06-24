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

import logging

from fastapi import APIRouter, HTTPException
from loguru import logger
from starlette.status import HTTP_404_NOT_FOUND

from api.utils import create_request_coroutine
from core.config import REFGET_SERVER_URL_LIST
from core.logging import InterceptHandler

logging.getLogger().handlers = [InterceptHandler()]

router = APIRouter()


@router.get("/{checksum}", name="sequence")
async def get_sequence(checksum: str, start: str = "", end: str = ""):
    """
    Return Refget sequence based on checksum value.
    str start: Start point of the sequence defined in checksum.
    str end: End point of the sequence defined in checksum.
    """
    headers = {"content-type": "accept=text/plain"}
    params = {}
    if int(start) < int(end):
        params = {"start": start, "end": end}
    url_path = "sequence/" + checksum
    try:
        result = await create_request_coroutine(
            url_list=metadata_url_list(checksum),
            url_path=url_path,
            headers=headers,
            params=params,
        )
        if result == "":
            return HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Not Found")

        return result
    except Exception as e:
        logger.log("DEBUG", "Unhandled exception in get_sequence" + str(e))


@router.get("/{checksum}/metadata", name="sequence:metadata")
async def get_sequence_metadata(checksum: str):
    """Return Refget sequence metadata based on checksum value."""

    headers = {"content-type": "accept=application/json"}

    url_path = "sequence/" + checksum + "/metadata"
    try:
        result = await create_request_coroutine(
            url_list=metadata_url_list(checksum),
            url_path=url_path,
            headers=headers,
            params="",
        )
        if result == "":
            return HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Not Found")
        return result
    except Exception as e:
        logger.log("DEBUG", "Unhandled exception in get_sequence_metadata" + str(e))


def metadata_url_list(checksum):
    """
    Create and return a list of tuples containing:
    [("Refget server URL", "Generated metadata URL ")]
    """

    url_list = [
        (url, url + "sequence/" + checksum + "/metadata")
        for url in REFGET_SERVER_URL_LIST
    ]
    return url_list
