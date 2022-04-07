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

import requests

from core.config import HTTP_LOGGING_URL


class JSONFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        record.msg = json.dumps(record.msg)
        return super().format(record)


formatter = logging.Formatter(json.dumps({
    'time': '%(asctime)s',
    'pathname': '%(pathname)s',
    'line': '%(lineno)d',
    'logLevel': '%(levelname)s',
    'message': '%(message)s'
}))


class InterceptHandler(logging.Handler):
    def send_request(self, url, log_entry):
        try:
            session = requests.Session()
            session.trust_env = False

            return session.post(url, log_entry, headers={"Content-type": "application/json"}, ).content

        except Exception as e:
            pass

    def refget_json_format(self, log_entry):
        try:
            log_entry = log_entry.replace("<CIMultiDictProxy(", '{')
            log_entry = log_entry.replace(')>', '}')
            log_entry = log_entry.replace("'", '"')
            log_entry = json.loads(log_entry)
            log_entry = log_entry["result"].pop("response", None)
            return json.dumps(log_entry)
        except Exception as e:
            return log_entry

    def emit(self, record: logging.LogRecord):  # pragma: no cover
        log_entry = self.format(record)
        url = HTTP_LOGGING_URL
        log_entry = self.refget_json_format(log_entry)
        return self.send_request(url, log_entry)


# create logger
log = logging.getLogger('')
log.setLevel(logging.INFO)

httpHandler = InterceptHandler()
httpHandler.setLevel(logging.INFO)
httpHandler.setFormatter(JSONFormatter())
log.addHandler(httpHandler)

# try:
#     level = logger.level(record.levelname).name
# except ValueError:
#     level = str(record.levelno)
#
# frame, depth = logging.currentframe(), 2
# while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
#     frame = cast(FrameType, frame.f_back)
#     depth += 1
#
# logger.opt(depth=depth, exception=record.exc_info).log(
#     level,
#     record.getMessage(),
# )
