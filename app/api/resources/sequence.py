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
    try:
        query_string = "?"
        if start < end:
            query_string = f"?start={start}&end={end}&"
        query_string = "sequence/" + checksum + query_string + "accept=text/plain"
        result = await create_request_coroutine(
            metadata_url_list(checksum), query_string
        )
        if result == "":
            return HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Not Found")

        return result
    except Exception as e:
        logger.log("INFO", "Unhandled exception in get_sequence" + str(e))


@router.get("/{checksum}/metadata", name="sequence:metadata")
async def get_sequence_metadata(checksum: str):
    """Return Refget sequence metadata based on checksum value."""

    try:
        query_string = "sequence/" + checksum + "/metadata?accept=application/json"
        result = await create_request_coroutine(
            metadata_url_list(checksum), query_string
        )
        if result == "":
            return HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Not Found")
        return result
    except Exception as e:
        logger.log("INFO", "Unhandled exception in get_sequence_metadata" + str(e))


def metadata_url_list(checksum):
    """
    Create and return a list of tuples containing:
    [("Refget server URL", "Generated metadata URL ")]
    """

    url_list = [
        (url, url + "sequence/" + checksum + "/metadata?accept=application/json")
        for url in REFGET_SERVER_URL_LIST
    ]
    return url_list
