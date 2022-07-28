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

import socket
import sys
from logging.handlers import SocketHandler
from os import environ
from typing import List

from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings
import logging.config
import logging.handlers

VERSION = "0.0.0"
API_PREFIX = "/api"

REFGET_SERVER_URL_LIST: List[str] = list(
    environ.get("REFGET_SERVER_URL_LIST", "").split(",")
)
REFGET_SERVER_URL_LIST_NO_PROXY: List[str] = list(
    environ.get("REFGET_SERVER_URL_LIST_NO_PROXY", "").split(",")
)
REDIS_HOST: str = environ.get("REDIS_HOST", "redis")
REDIS_PORT: str = environ.get("REDIS_PORT", "6379")

config = Config(".env")
DEBUG: bool = config("DEBUG", cast=bool, default=True)
PROJECT_NAME: str = config("PROJECT_NAME", default="Ensembl Refget Proxy")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="*",
)

# logging configuration


LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "gunicorn.access")

for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

HTTP_PROXY = environ.get("HTTP_PROXY", "")
HTTPS_PROXY = environ.get("HTTPS_PROXY", "")
