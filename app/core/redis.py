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
import json

import aioredis
from loguru import logger

from core.config import REDIS_HOST, REDIS_PORT, REFGET_SERVER_URL_LIST_NO_PROXY


class RedisConnection(object):
    """
    Context manager to handle async redis connections.
    """

    def __init__(self):
        """
        redis_connection_info: Add password or port number and create a connection string.
        Example:
         pass db index: redis://REDIS_HOST/2
         password: redis://REDIS_HOST/?password=yourredispass
         port: redis://REDIS_HOST:6379
        """
        self.redis_connection_info = REDIS_HOST + ":" + REDIS_PORT
        self.redis_connection = aioredis.create_redis_pool(
            "redis://" + self.redis_connection_info, timeout=10
        )

    async def __aenter__(self):
        self.redis_connection = await self.redis_connection
        return self.redis_connection

    async def __aexit__(self, exc_type, exc, tb):
        self.redis_connection.close()


async def cache_url(url_detail):
    """
    Store url in redis using checksum as key.
    """
    try:
        async with RedisConnection() as redis:
            await asyncio.ensure_future(
                redis.set(url_detail["checksum"], url_detail["refget_server_url"])
            )
        return True
    except Exception as e:
        logger.log("DEBUG", "UNHANDLED EXCEPTION" + str(e))
        return False


async def get_cached_url(checksum):
    """
    Get cached url from redis.
    """
    try:
        url_result = {}
        async with RedisConnection() as redis:
            url = await asyncio.ensure_future(redis.get(checksum, encoding="utf-8"))
            if url:
                url_result = {
                    "refget_server_url": url,
                    "checksum": checksum,
                    "metadata_url": url + "sequence/" + checksum + "/metadata",
                    "use_proxy": True
                }
                if url in REFGET_SERVER_URL_LIST_NO_PROXY:
                    url_result["use_proxy"] = False
            return url_result
    except Exception as e:
        logger.log("DEBUG", "UNHANDLED EXCEPTION" + str(e))
        return {}


async def cache_metadata(url_detail, metadata):
    """
    Store metadata in redis using checksum/metadata as key.
    """
    try:
        async with RedisConnection() as redis:
            await asyncio.ensure_future(
                redis.set(url_detail["checksum"] + "/metadata", json.dumps(metadata))
            )
        return True
    except Exception as e:
        logger.log("DEBUG", "UNHANDLED EXCEPTION" + str(e))
        return False


async def get_cached_metadata(checksum):
    """
    Get cached metadata from redis.
    """
    try:
        async with RedisConnection() as redis:
            result = await asyncio.ensure_future(redis.get(checksum + "/metadata"))
            if result:
                return json.loads(result, encoding="utf-8")

    except Exception as e:
        logger.log("DEBUG", "UNHANDLED EXCEPTION" + str(e))
        return {}
