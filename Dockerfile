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

FROM tiangolo/uvicorn-gunicorn:python3.8
ENV PORT 8083
ENV REFGET_SERVER_URL_LIST https://www.ebi.ac.uk/ena/cram/,http://refget.herokuapp.com/
EXPOSE 8083
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# RUN mkdir app

# WORKDIR /app

COPY ./app/ /app/

COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.0.* && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# CMD gunicorn -w 4 --bind=0.0.0.0:8083 --preload -t 120 main:app uvicorn.workers.UvicornWorker