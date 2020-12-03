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

from starlette.responses import PlainTextResponse
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
    HTTP_400_BAD_REQUEST,
    HTTP_501_NOT_IMPLEMENTED,
)


def response_error_handler(result):
    if result["status"] == 501:
        return http_501_not_implemented()
    if result["status"] == 416:
        return http_416_range_not_satisfied()
    if result["status"] == 406:
        return http_406_not_acceptable()
    if result["status"] == 400:
        return http_400_bad_request()
    if result["status"] == 501:
        return http_501_not_implemented()
    if result["status"] == 404:
        return http_404_not_found()
    else:
        return http_unknown_error(result)


def http_unknown_error(result):
    response_msg = json.dumps({"status_code": result["status"], "details": "Unknown"})
    return PlainTextResponse(response_msg, status_code=result["status"])


def http_400_bad_request():
    response_msg = json.dumps(
        {"status_code": HTTP_400_BAD_REQUEST, "details": "Bad Request"}
    )
    return PlainTextResponse(response_msg, status_code=HTTP_400_BAD_REQUEST)


def http_404_not_found():
    response_msg = json.dumps(
        {"status_code": HTTP_404_NOT_FOUND, "details": "Not Found"}
    )
    return PlainTextResponse(response_msg, status_code=HTTP_404_NOT_FOUND)


def http_406_not_acceptable():
    response_msg = json.dumps(
        {"status_code": HTTP_406_NOT_ACCEPTABLE, "details": "Not Acceptable"}
    )
    return PlainTextResponse(response_msg, status_code=HTTP_406_NOT_ACCEPTABLE)


def http_416_range_not_satisfied():
    response_msg = json.dumps(
        {
            "status_code": HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            "details": "Request Range Not Satisfied",
        }
    )
    return PlainTextResponse(
        response_msg, status_code=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
    )


def http_501_not_implemented():
    response_msg = json.dumps(
        {"status_code": HTTP_501_NOT_IMPLEMENTED, "details": "Not Implemented",}
    )
    return PlainTextResponse(response_msg, status_code=HTTP_501_NOT_IMPLEMENTED)
