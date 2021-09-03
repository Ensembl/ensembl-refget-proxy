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

import logging
import socket
import sys
from logging.handlers import SocketHandler
from os import environ
from typing import List

import requests
from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

from .logging import InterceptHandler

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

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"default": {"format": "%(asctime)s [%(process)s] %(levelname)s: %(message)s"}},
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "INFO",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
    },
}
import logging.config
import logging.handlers
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "gunicorn.access")

logging.config.dictConfig(LOG_CONFIG)
log = logging.getLogger("gunicorn.access")
udp_handler_host: str = environ.get("UDP_HANDLER_HOST", "localhost")
udp_handler_port: int = int(environ.get("UDP_HANDLER_PORT", 8081))
udp_handler = logging.handlers.SysLogHandler(address=(udp_handler_host, udp_handler_port), socktype=socket.SOCK_DGRAM)

udp_handler.setLevel(LOGGING_LEVEL)
logging.getLogger().handlers = [udp_handler]

log.addHandler(udp_handler)


logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

HTTP_PROXY = environ.get("HTTP_PROXY", "")
HTTPS_PROXY = environ.get("HTTPS_PROXY", "")
